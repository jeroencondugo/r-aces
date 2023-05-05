
import datetime as datetime
import gc
import io
import os
import warnings
from typing import List, Tuple, Optional, Dict, Union

import pandas as pd
import redis
import redis_lock
from pymemcache.client import base as mc_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, orm
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict, MutableList

from cdglib.common_funcs import get_all_subclasses
from cdglib.config import ConfigFactory
from cdglib.df_manipulator import DataframeManipulator as DFM
from cdglib.init_lib import logger
from cdglib.cdglogging import deprecated
from cdglib.measure import MeasureRegister
from cdglib.models_client.meter_configs import MeterConfig

redis_lock_cfg = ConfigFactory.create_lock_redis_config(ConfigFactory.default_config_path())
redis_lock_blocking = False
redis_lock_default_timeout = 900
memcache_default_expire = 900
use_memcached = False



meter_ids = []


class MeterBase(object):
    """
    Represents a meter, which can provide measurements.
    Each meter belongs to a maximum of one commodity type PER SITE HIERARCHY.
    Similarly, each meter belongs to a maximum of one site PER SITE HIERARCHY.
    """

    # -----------------------------------------------------------------------
    # Columns

    @declared_attr
    def id(self):
        return Column(Integer, primary_key=True, )

    measure_id = Column(Integer, index=True)
    name = Column(String, index=True)
    meter_type = Column(Integer, index=True)
    disposed = Column(Boolean, default=False, nullable=False, index=True)
    changed = Column(Boolean, index=True)
    changed_at = Column(DateTime, default=datetime.datetime.now)
    #sparkline = Column(MutableDict.as_mutable(JSONB), default=MutableDict())

    mc_client = mc_base.Client(('localhost', 11211))
    message_tree = Column(MutableDict.as_mutable(JSONB), default=MutableDict())
    message_summary = Column(MutableList.as_mutable(JSONB), default=MutableList())
    import_uuid = Column(String, index=True)

    # -----------------------------------------------------------------------
    # Public methods

    def __init__(self, name, measure):
        self.name = name
        # self.category=category
        if measure:
            self.measure_id = measure.id
        self.reinit()

    @orm.reconstructor
    def reinit(self):
        self.verbose = False

    def add_config_to_chart(self, meter_config):
        """ Add a config to this meter's chart. """
        meter_config.meter = self

    def set_source_config(self, meter_config):
        print("set source config cdglib")
        self.source_config = meter_config

    @property
    def measure(self):
        return self.get_measure()

    def get_measure(self):
        return MeasureRegister.get_id(self.measure_id) if self.measure_id else None

    @property
    def measure_name(self):
        return MeasureRegister.get_id(self.measure_id).name if self.measure_id else "unknown"

    def get_last_timestamp(self):
        """
        Return a datetime object of the last data entry, or None if empty.
        """
        ts = None
        for cfg in self.configs:
            d = cfg.get_last_timestamp()  # TODO: This is not a valid method of meterconfig
            if ts is None or d > ts: ts = d
        return ts

    def get_extent(self):
        """
        Return a tuple of two datetime objects.
        """
        if self.source_config:
            return self.source_config.get_extent()
        return None, None

    @deprecated("Use MeterDataService instead of this method!")
    def get_data(self, begin: datetime, end: datetime, client_schema: Optional[str] = None, data_timezone: str = "UTC", agg_timezone: str = "UTC"):
        """
        Return a pandas dataframe with columns "ts","val".

        First check memcached for recent dataframe and if not found:
        - acquire lock on meter
        - get dataframe from database
        - release lock

        begin: inclusive start of the requested data in the data_timezone timezone
        end: exclusive end of the requested data in the data_timezone timezone
        data_timezone: timezone into which resulting data (frame) is converted to
        agg_timezone: timezone used for aggregation, for example hourly data is aggregated to daily data so it
        determines which hours aggregate into a day
        """
        logger.debug(f"Getting data for meter {self.id}:{self.name}")

        dt_tz = str(data_timezone)
        agg_tz = str(agg_timezone)

        if begin:
            begin = pd.to_datetime(begin)

            if begin.tzinfo is None or begin.tzinfo.utcoffset(begin) is None:
                # if begin is in naive format - localize
                begin = begin.tz_localize(dt_tz)

            begin = begin.tz_convert("UTC")

        if end:
            end = pd.to_datetime(end)

            if end.tzinfo is None or end.tzinfo.utcoffset(end) is None:
                # if end is in naive format - localize
                end = end.tz_localize(dt_tz)

            end = end.tz_convert("UTC")

        #key_touched = raw_input()
        def cache_df(name, df):
            df_feather = df.copy()
            df_feather.reset_index(inplace=True)
            buf = io.BytesIO()
            df_feather.to_feather(buf, version=1)
            self.mc_client.set(name, buf.getvalue(), expire=memcache_default_expire)

        def decache(name):
            df=None
            if self.mc_client:
                df_bytes = self.mc_client.get(name)
                if df_bytes:
                    bytes_buf = io.BytesIO(df_bytes)
                    df = pd.read_feather(bytes_buf, use_threads=False)
                    df.set_index('ts', inplace=True)
            return df

        df = None
        # Check memcache for recent dataframe
        lock_name = '{}_{}_meter_get_data_{}'.format(os.environ.get('CONDUGO_ENV', 'dev'), client_schema, self.id)
        if use_memcached:
            df_cache = decache(lock_name)
            if df_cache:
                return df_cache

        # Acquire lock on meter
        if redis_lock_blocking:
            redis_connection = redis.Redis(host=redis_lock_cfg.host, port=redis_lock_cfg.port,
                                           username=redis_lock_cfg.username, password=redis_lock_cfg.password, ssl=True,
                                           ssl_ca_certs=redis_lock_cfg.ca_path, db=redis_lock_cfg.db)
            lock = redis_lock.Lock(redis_connection, lock_name)
        if redis_lock_blocking:
            if lock.acquire(blocking=redis_lock_blocking, timeout=redis_lock_default_timeout):
                try:
                    # Get dataframe from meter
                    df = self.source_config.get_data(begin, end, agg_tz) if self.source_config else None
                    df = DFM.convert_from_utc_to_tz(df, dt_tz)
                    if df.index.tz is not None:
                        df.index = df.index.tz_localize(None)

                    if use_memcached:
                        cache_df(lock_name, df)
                except Exception:
                    pass
                finally:
                    # Release lock on meter
                    lock.release()
        else:
            df = self.source_config.get_data(begin, end) if self.source_config else None
            df = DFM.convert_from_utc_to_tz(df, dt_tz)
            if df is not None and df.index is not None and df.index.tz is not None:
                df.index = df.index.tz_localize(None)

        if redis_lock_blocking: redis_connection.close()
        gc.collect()
        return df

    def check_circular_meter_references(self, parent_meters:List[Tuple[int, str]]):
        """ Check for MeterConfigMeters who refer to meter_ids which are in the list of parent meter ids """
        messages = []
        mcms = [mc for mc in self.configs if mc.discriminator == 'MeterConfigMeter']
        parent_meters.append((self.id, self.name))
        circular_meter_ids = [pm[0] for pm in parent_meters]
        circular_meter_name_per_id = {pm[0]: pm[1] for pm in parent_meters}
        for mcm in mcms:
            if mcm.source_meter_id in circular_meter_ids:
                # Circular dependency detected
                ref_meter = mcm.source_meter.name if mcm.source_meter else None
                messages.append(f"Circular meter reference detected: MeterConfigMeter {mcm.name} in meter {self.name} referring to meter {ref_meter} which is a parent meter!")
                # Do NOT recurse down circular route
            else:
                # Recurse
                if mcm.source_meter:
                    messages += mcm.source_meter.check_circular_meter_references(parent_meters)
        return messages

    # def get_configs(self):
    #    return self.configs.all()

    def get_message_tree(self):
        """ Return the message tree from the configs """
        output = {
            "id": self.id,
            "name": self.name,
            "type": self.__class__.__name__,
            "messages": [],
            "input_configs": [],
        }
        if self.source_config:
            output['input_configs'].append(self.source_config.get_message_tree())
            if self.measure_id != self.source_config.measure_id:
                output['messages'].append(f"Meter {self.name}({self.id}) measure ({self.measure_name}) does not equal source config measure ({self.source_config.measure_name})!")
            if output['input_configs'] or output['messages']:
                return output
            else:
                return None
        else:
            output['messages'].append(f"Meter {self.name}({self.id}) has no source config")
            return output

    def register_config(self, config):
        self.configs.append(config)

    def get_commodity_type(self):
        #ct = self.sites.filter_by(discriminator='CommodityType').first()
        ct = [ct for ct in self.sites if ct.__class__.__name__ == 'CommodityType'][0]
        return ct

    def write_values(self, ts, vals):
        """
        Add new values to the meter.
        ts: A list of datetime objects
        vals: A list of float values
        """
        if not self.write_config:
            raise Exception("Unable to write values, no write config defined")
        if not self.write_config.is_writeable():
            raise Exception("Unable to write values, meter config is not writeable")
        self.write_config.write_values(ts, vals)

    def add_values(self, sh, values):
        warnings.warn("deprecated, use write_values instead", DeprecationWarning)
        mc = sh.query(MeterConfig).get(self.write_config_id)
        mc.add_values(sh, values)


    def to_dict(self):
        """ convert Meter object to dict without the configs """
        return {
            "id": self.id,
            "measure_id": self.measure_id,
            "name": self.name,
            "meter_type": self.meter_type,
            "disposed": self.disposed,
            "changed": self.changed.isoformat() if self.changed else None,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            #"sparkline": self.sparkline,
            "message_tree": self.message_tree,
            "message_summary": self.message_summary,
            "organisation_id": self.organisation_id,
            "source_config_id": self.source_config_id,
            "configs": [mc.to_dict() for mc in self.configs]
        }
