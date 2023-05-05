#  Copyright (c) 2015-2022 Condugo bvba

import json
import math
import os
import uuid
import dateutil
from datetime import datetime
from io import StringIO
from typing import List, Optional, Any, Tuple

import numpy as np
import pandas as pd
from slugify import slugify

from cdglib.models_client import NodeLevel
from dateutil.parser import ParserError
from sqlalchemy.ext.mutable import MutableDict, MutableList

from cdg_service.service.basetree import BasetreeService
from cdg_service.service.basetree_level import BasetreeLevelService
from cdg_service.service.basetree_node import BasetreeNodeService
from cdg_service.service.common.base_service import Service
from cdg_service.service.historian import HistorianService
from cdg_service.service.meter import MeterService, MeterNodeChangesPayload, MeterNodeChange
from cdg_service.service.meter_model.meter_model_service import MeterModelService
from cdglib import get_all_subclasses
from cdglib.measure import MeasureRegister, InterpolationStrategy
from cdglib.models_domain.meter_configs.meter_config_dataclasses import MeterConfigHistorian
from cdglib.models_domain.meter_data_classes import MetersExport
import cdglib.influx.influx_manager as influx_manager
from cdglib.utils.df_utils.manipulations.sync_and_interpolate import SyncAndInterpolate


class MeterImportExportService(Service):

    def __init__(self, session=None, config=None):
        """ Constructor """
        super().__init__(session, config)
        self.bt_lvl_svc = BasetreeLevelService(self.session)
        self.bt_svc = BasetreeService(self.session)
        self.bt_node_svc = BasetreeNodeService(self.session)

    def create(self, **kwargs):
        raise NotImplementedError()

    def read(self, **kwargs):
        raise NotImplementedError()

    def update(self, **kwargs):
        raise NotImplementedError()

    def delete(self, meter_id):
        raise NotImplementedError()

    def search(self, param):
        raise NotImplementedError

    def load_excel_as_df(self, filename: str, sheetname: str) -> Tuple[
        Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """ Load excel file sheet into a dataframe """
        with open(filename, "rb") as f:
            df = pd.read_excel(io=f, sheet_name=sheetname, index_col=0)
        df_meters = df.head(2)
        index_list = df.index.to_list()
        start_dt_index = None
        for idx, value in enumerate(index_list):
            if isinstance(value, datetime):
                start_dt_index = idx
                break
            elif isinstance(value, str):
                try:
                    dt_value = dateutil.parser.parse(timestr=value, yearfirst=True, dayfirst=False)
                except (ParserError, OverflowError) as e:
                    dt_value = None
                if dt_value:
                    start_dt_index = idx
                    break
        df_bt_nodes = None
        if start_dt_index and start_dt_index > 2:
            df_bt_nodes = df[2:start_dt_index]
        df_ts_data = df[start_dt_index: len(df.index)]
        return df_meters, df_bt_nodes, df_ts_data

    def export_meters_pandas(self, meter_ids: List[int]) -> pd.DataFrame:
        """ export meters within the list of meter_ids to a pandas dataframe """
        raise NotImplementedError()

    def import_meters_pandas(self, df_meters: pd.DataFrame, df_bt_nodes: pd.DataFrame, df_ts_data: pd.DataFrame,
                             replace_import_uuid: Optional[str], uuid_filename: str="", delete_all_meters: bool=False) -> str:
        """ Import meters from three pandas dataframes
            The pandas dataframe can originate from a CSV file or an Excel or Google Sheets.
            The format expected is as follows:
            df_meters:
            - columns have meter names which are the identifiers
            - index measure contains measure ids for each meter

            df_bt_nodes:
            - columns have meter names which are the identifiers
            - indexes contain the bt levels names
            - values are the associated bt node in the bt level of the index

            df_ts_data:
            - columns have meter names which are the identifiers
            - indexes contain the timestamp in UTC for the values
            - indexes are in old to new order
        """
        if replace_import_uuid:
            self.__delete_meters_from_import_uuid(replace_import_uuid, all_meters=delete_all_meters)
        import_uuid = uuid.uuid4()
        if uuid_filename:
            with open(uuid_filename, "w") as impf:
                impf.write(str(import_uuid))
        created_mtrs = None
        if df_meters is not None:
            created_mtrs = self.__import_df_meters(df_meters, str(import_uuid))
            print(f"No. of meters created: {len(created_mtrs)}")
        if df_bt_nodes is not None:
            self.__import_df_bt_nodes(df_bt_nodes, created_mtrs=created_mtrs)
        if df_ts_data is not None:
            self.__import_df_ts_data(df_ts_data)
        return import_uuid

    def __delete_meters_from_import_uuid(self, import_uuid: str, all_meters: bool=False):
        """ Delete all meters with import_uuid property set to import_uuid """
        mtr_svc = MeterService(self.session)
        if all_meters:
            mtrs = mtr_svc.read()
        else:
            mtrs = mtr_svc.read(import_uuid=import_uuid)
        for mtr in mtrs:
            # print(f"Deleting {mtr.name}: {mtr.id}: {mtr.import_uuid}")
            mtr_svc.delete(mtr.id)
            self.session.commit()

    def __import_meter(self, meter_name: str, measure_id: int, import_uuid: str, apply_delta: bool):
        """ Import a single meter """
        mtr_svc = MeterService(self.session)
        mtr_mdl_svc = MeterModelService(self.session)
        if not self.__validate_measure_id(measure_id):
            measure_id = None
        if not self.__validate_meter_name(meter_name):
            raise ValueError(f"Meter with {meter_name} already exists!")
        mtr_payload = {
            "name": meter_name,
            "measure_id": measure_id,
            "import_uuid": import_uuid,
            "changes": [
            ]
        }
        mtr = mtr_svc.create(**mtr_payload)
        self.session.commit()
        if mtr:
            # Add the meter models
            mtr_mdl_payload = self.__create_meter_model_historian_changeset_payload(mtr.id, mtr.name, mtr.name,
                                                                                    mtr.measure_id, apply_delta)
            changeset = mtr_mdl_svc.apply_changeset(mtr.id, mtr_mdl_payload)
            self.session.commit()
        return mtr

    def __create_meter_model_historian_changeset_payload(self, meter_id: int, name: str, table_name: str,
                                                         measure_id: int, apply_delta: bool):
        """ Create meter model changeset payload for a single meter model historian """
        return {
            "id": meter_id,
            "connected_port": None,
            "configs": {
                "update": [
                    {
                        "id": f"meter_{meter_id}",
                        "input_ports": [
                            {
                                "id": f"meter_{meter_id}",
                                "graph_node_id": f"meter_{meter_id}",
                                "output_port_id": "new_1_0",
                                "output_node_id": "new_1"
                            }
                        ]
                    }
                ],
                "create": [
                    {
                        "id": "new_1",
                        "type": "MeterModelHistorian",
                        "catalog_id": "historianSource",
                        "input_ports": [

                        ],
                        "output_ports": [
                            {
                                "id": "new_1_0",
                                "name": "",
                                "graph_node_id": "new_1"
                            }
                        ],
                        "name": name,
                        "table_name": self.__format_table_name(table_name),
                        "measure_id": measure_id,
                        "apply_delta": apply_delta
                    }
                ],
                "remove": []
            }
        }

    def __import_df_meters(self, df_meters: pd.DataFrame, import_uuid: str):
        """ Import all meters based on the pandas df_meters DataFrame """
        created_mtrs = []
        for meter_name in df_meters:
            print(f"Processing column: {df_meters[meter_name]}")
            try:
                measure_txt = df_meters.at["Measure", meter_name]
            except KeyError:
                measure_txt = ""
            if isinstance(measure_txt, str) and " - " in measure_txt:
                measure_id, measure_description = measure_txt.split(' - ')
                measure_id = int(measure_id)
            else:
                measure_id = None
            try:
                apply_delta = df_meters.at["Increasing values", meter_name]
            except KeyError:
                apply_delta = False
            mtr = self.__import_meter(meter_name, measure_id, import_uuid, apply_delta)
            created_mtrs.append(mtr)
        return created_mtrs

    def __validate_meter_name(self, meter_name: str) -> bool:
        mtr_svc = MeterService(self.session)
        mtrs = mtr_svc.read()
        mtr_names = [mtr.name for mtr in mtrs]
        if meter_name in mtr_names:
            return False
        return True

    def __validate_measure_id(self, measure_id: int) -> bool:
        try:
            measure = MeasureRegister.get_id(measure_id)
            return True
        except Exception:
            return False

    def __import_df_bt_nodes(self, df_bt_nodes: pd.DataFrame, created_mtrs: List[Any]):
        """ Connect meters to the correct basetree nodes """
        Basetree = self._classmap.Basetree
        NodeLevel = self._classmap.NodeLevel
        Node = self._classmap.Node
        bts = BasetreeService(self.session)
        btls = BasetreeLevelService(self.session)
        btns = BasetreeNodeService(session=self.session, config=None)
        mncp = MeterNodeChangesPayload()
        mtr_svc = MeterService(self.session)
        if not created_mtrs:
            created_mtrs = mtr_svc.read()
        mtr_by_name = {mtr.name: mtr for mtr in created_mtrs}
        failed_links = []
        for meter_name in df_bt_nodes:
            mtr = mtr_by_name.get(meter_name)
            for bt_level_name in df_bt_nodes.index.to_list():
                bt_level_name = bt_level_name.strip()
                if bt_level_name in ("Region", "Country", "Subregion"):
                    continue
                if not btls.exists(bt_level_name):
                    failed_links.append({"meter": meter_name, "level_name": bt_level_name, "node_name": None,
                                         "reason": f"level_name {bt_level_name} not found!"})
                    # raise ValueError(f"Basetree level with name {bt_level_name} does not exist!")
                bt_level = self.session.query(NodeLevel).filter(NodeLevel.name == bt_level_name).first()
                node_name = df_bt_nodes.at[bt_level_name, meter_name]
                node_name = node_name.strip()
                if not btns.exists(node_name):
                    if node_name == np.nan or node_name is None or (isinstance(node_name, float) and math.isnan(node_name)): continue
                    failed_links.append({"meter": meter_name, "level_name": bt_level_name, "node_name": node_name,
                                         "reason": f"node_name {node_name} not found!", "type": str(type(node_name))})
                    continue
                    # raise ValueError(f"Basetree node with name {node_name} does not exist!")
                nodes = btns.read(name=node_name)
                node = nodes[0]
                if node is None:
                    print(node_name)
                if mtr is None:
                    print(f"Meter: {meter_name}")
                bt = node.hierarchy
                mnc = MeterNodeChange(basetree_id=bt.id, meter_id=mtr.id, node_id=node.id)
                mncp.changes.append(mnc)

        mtr_svc.apply_node_changes(mncp)
        for fl in failed_links:
            print(fl)

    def __validate_bt_level(self, bt_level: str) -> bool:
        """ Check if the bt_level exists """
        return self.bt_lvl_svc.exists(bt_level)

    def __validate_bt_level_node(self, bt_level: str, bt_node: str) -> bool:
        """ Check if the bt_node exists on the bt_level """
        bt_lvl: NodeLevel = self.bt_lvl_svc.read(name=bt_level)
        bt_lvl_nodes = bt_lvl.get_sites()
        if self.bt_node_svc.exists(bt_node):
            btn = self.bt_node_svc.read(name=bt_node)
            if btn and btn in bt_lvl_nodes:
                return True
        return False

    def __import_df_ts_data(self, df_ts_data: pd.DataFrame):
        """ Write the time series data to the influxdb """
        for name, col in df_ts_data.iteritems():
            col.fillna(0.0, inplace=True)
            bucket_name = f"%ENV%-m_{self.client_id}"
            drop_bucket_name = bucket_name.replace('%ENV%', os.environ.get('CONDUGO_ENV'))
            measurement_name = self.__format_table_name(name)
            # Delete old measurement
            influx_manager.drop_measurement(drop_bucket_name, measurement_name)
            col.name = 'value'
            df = col.to_frame()
            df = influx_manager.convert_nan_inf_bool_to_float(df)
            dfint = SyncAndInterpolate(interpolation_strategy=InterpolationStrategy.UNDER_INTEGRAL)
            df = dfint.manipulate(df)
            influx_manager.write(data=df, bucket_name=bucket_name, measurement_name=measurement_name,
                                 column_name='value')
            import time
            time.sleep(0.5)

    def export_meters_excel(self, meter_ids: Optional[List[int]] = None):
        """ export meters to an excel with the measures and basetree connections in place """
        mtr_svc = MeterService(self.session)
        bt_svc = BasetreeService(self.session)
        btl_svc = BasetreeLevelService(self.session)
        btn_svc = BasetreeNodeService(self.session)
        meters = mtr_svc.read(meter_ids=meter_ids)

    def export_meters_json(self, meter_ids: List[int]) -> MetersExport:
        """ export meters with ids in meter_ids to a list of dataclasses."""
        meters = self.read(meter_ids=meter_ids, configs=True)
        for m in meters[:1]:
            for c in m.configs[:1]:
                from pprint import pprint
                pprint(c.to_dict())
                mc = MeterConfigHistorian(**c.to_dict())
        # export historians and nested meters as well
        all_meters = set(meters)
        all_nested_meters = set()
        for m in meters:
            nested_meters = self._find_nested_meters(m)
            all_nested_meters = all_nested_meters.union(nested_meters)
        all_meters = all_meters.union(all_nested_meters)
        historians = set()
        for m in meters:
            m_historians = self._find_historians(m)
            historians = historians.union(m_historians)

        medc_dict = {
            "meters": [m.to_dict() for m in all_meters],
            "historians": [h.to_dict() for h in historians]
        }
        medc = MetersExport(**medc_dict)
        return medc

    def import_meters_json(self, json_string: str):
        """ Import meters from a json string """
        # Convert json string to objects
        data = json.load(StringIO(json_string))
        medc = MetersExport(**data)
        # Fetch organisation
        org = self.session.query(self._classmap.Organisation).first()
        # Setup historians if they do not exist
        known_historians = self.session.query(self._classmap.Historian).all()
        known_historian_identifiers = {h.identifier: h for h in known_historians}
        historians_per_id = {}
        for hist in medc.historians:
            if hist.identifier in known_historian_identifiers:
                historians_per_id[hist.id] = known_historian_identifiers[hist.identifier]
            else:
                # Create historian
                new_historian = self._classmap.Historian()
                new_historian.organisation_id = org.id
                new_historian.type = hist.type
                new_historian.server = hist.server
                new_historian.port = hist.port
                new_historian.db_name = hist.db_name
                new_historian.username = hist.username
                new_historian.password = hist.password
                new_historian.default_time_column_name = hist.default_time_column_name
                new_historian.default_value_column_name = hist.default_value_column_name
                self.session.add(new_historian)
                self.session.flush()
                historians_per_id[hist.id] = new_historian
        # Create meters and meter_configs
        known_meters = self.session.query(self._classmap.Meter).all()
        known_meters_by_name = {m.name: m for m in known_meters}
        for mtr in medc.meters:
            print("&" * 20, "Importing", mtr.name)
            # Setup new meter object
            new_mtr = self._classmap.Meter()
            new_mtr.organisation_id = org.id
            new_meter_name = mtr.name
            # If meter with this name exist add imported to the name
            if mtr.name in known_meters_by_name:
                new_meter_name = f"{mtr.name} (Imported)"
                # If meter with name including imported exists add counter starting at 2
                if new_meter_name in known_meters_by_name:
                    id = 2
                    while True:
                        new_meter_name_with_counter = f"{new_meter_name} {id}"
                        id += 1
                        if new_meter_name_with_counter not in known_meters_by_name:
                            break
                    new_meter_name = new_meter_name_with_counter
            new_mtr.name = new_meter_name
            new_mtr.measure_id = mtr.measure_id
            new_mtr.changed = mtr.changed
            new_mtr.changed_at = datetime.utcnow()
            new_mtr.meter_type = mtr.meter_type
            new_mtr.verbose = False
            if not mtr.message_tree:
                new_mtr.message_tree = MutableDict()
            else:
                new_mtr.message_tree = mtr.message_tree
            if not mtr.message_summary:
                new_mtr.message_summary = MutableList()
            else:
                new_mtr.message_summary = mtr.message_summary
            new_mtr.disposed = False
            new_mtr.source_config_id = None
            new_mtr.write_config = None
            new_mtr.configs = []
            self.session.add(new_mtr)
            self.session.flush()
            # Setup meter configs
            all_mc_sub_classes = get_all_subclasses(self._classmap.MeterConfig)
            sub_classes_by_name = {mcc.__name__: mcc for mcc in all_mc_sub_classes}
            new_config_by_id = {}
            config_by_id = {cfg.id: cfg for cfg in mtr.configs}
            for cfg in mtr.configs:
                print("$" * 20, "Importing config", cfg.name, " - ", cfg.type)
                # create config
                mc_class = sub_classes_by_name.get(cfg.type)
                if not mc_class:
                    raise TypeError(f"Meter config type {cfg.type} not recognised")
                new_mc = mc_class()
                # Fetch all attributes of new_mc which we need to set which are not internals or callables (methods)
                new_mc_attrs = self._get_mc_attrs(new_mc)
                for attr in new_mc_attrs:
                    if hasattr(cfg, attr):
                        if attr in ("id", "catalog_id", "historian_id", "historian"): continue
                        if attr.startswith("port_"): continue
                        if attr == "regular_data":
                            print(attr, "set to", getattr(cfg, attr))
                        try:

                            setattr(new_mc, attr, getattr(cfg, attr))
                            if attr == "regular_data":
                                print(attr, "has been set to", getattr(new_mc, attr))
                        except AttributeError as e:
                            print(f"Can't set attribute: {attr}, trying _{attr}")
                            # Try with adding a _ before the attr, so interval -> _interval
                            try:
                                new_value = getattr(cfg, attr)
                                setattr(new_mc, f"_{attr}", new_value)
                            except AttributeError as e:
                                print(f"Can't set attribute: _{attr}")
                    if hasattr(new_mc, "schema") and hasattr(cfg, "hist_schema"):
                        setattr(new_mc, "schema", getattr(cfg, "hist_schema"))
                new_mc.meter = new_mtr
                self.session.add(new_mc)
                self.session.flush()
                new_config_by_id[cfg.id] = new_mc

            # now attach meter configs to the ports of other meterconfigs
            for cfg in mtr.configs:
                new_mc = new_config_by_id.get(cfg.id)
                port_attrs = self._get_mc_port_attrs(new_mc)
                print(f"Port attrs: {port_attrs}")
                for pattr in port_attrs:
                    new_mc_attached_to_port = new_config_by_id.get(getattr(cfg, pattr))
                    if new_mc_attached_to_port:
                        print(
                            f"Connecting {new_mc.name}-{pattr} to {new_mc_attached_to_port.id} - {getattr(cfg, pattr)}")
                        setattr(new_mc, pattr, new_mc_attached_to_port.id)
                # Setup historian
                if hasattr(new_mc, "historian_id") and hasattr(cfg, "historian_id"):
                    new_mc.historian = historians_per_id.get(cfg.historian_id)
            # Setup source config on meter
            new_source_mc = new_config_by_id.get(mtr.source_config_id)
            if new_source_mc:
                new_mtr.source_config = new_source_mc

            self.session.commit()

    def _get_mc_attrs(self, meter_config):
        """ Return all attrutes for a meter config to set """
        return [attr for attr in dir(meter_config) if
                not (attr.startswith('__') or attr.startswith('_')) and not callable(getattr(meter_config, attr))]

    def _get_mc_port_attrs(self, meter_config):
        """ Return all attrutes for a meter config to set """
        return [attr for attr in dir(meter_config) if
                attr.startswith('port_') and attr.endswith('_id') and not callable(getattr(meter_config, attr))]

    def _find_historians(self, meter) -> set:
        """ Find all historians referenced in this meter """
        historian_ids = set()
        for c in meter.configs:
            if c.__class__.__name__ == "MeterConfigHistorian":
                historian_ids.add(c.historian_id)
        # load historians
        service = HistorianService(self.session)
        if historian_ids:
            historians = set(service.read(historian_ids=list(historian_ids)))
        else:
            historians = set()
        return historians

    def _find_nested_meters(self, meter) -> set:
        """ Find all historians referenced in this meter """
        source_meter_ids = set()
        for c in meter.configs:
            if c.__class__.__name__ == "MeterConfigMeter":
                source_meter_ids.add(c.source_meter_id)
        # load source_meters
        if source_meter_ids:
            source_meters = set(self.read(meter_ids=list(source_meter_ids), configs=True))
        else:
            source_meters = set()
        nested_meters = set()
        for source_meter in source_meters:
            sm_nested_meters = self._find_nested_meters(source_meter)
            nested_meters = nested_meters.union(sm_nested_meters)
        return source_meters.union(nested_meters)

    # ++++++++++++++++++++++++++++++++ Private methods ++++++++++++++++++++++++++

    def _meter_payload(self, name, measure_id, changes=[]):
        """ Helper function to build a create meter payload """
        return {
            "name": name,
            "measure_id": measure_id,
            "changes": changes
        }

    def _default_changeset_payload(self, meter_id, historian_id, measurement_name, measure_id, unit,
                                   time_col_name="timeStamp", \
                                   val_col_name="value", apply_delta=False, repeat_data=False, regular_data=True,
                                   synchronized_data=False, \
                                   interval="15T", timezone="Europe/Amsterdam"):
        """ Helper function to build a create default historian changeset payload """
        return {
            "id": meter_id,
            "source_config_id": "new_0",
            "configs": {
                "update": [],
                "create": [
                    {
                        "id": "new_0",
                        "type": "MeterConfigHistorian",
                        "catalog_id": "historianSource",
                        "input_ports": [],
                        "output_ports": [
                            {
                                "id": "new_0_0",
                                "name": "",
                                "graph_node_id": "new_0"
                            }
                        ],
                        "name": measurement_name,
                        "measure_id": measure_id,
                        "historian_id": historian_id,
                        "table": measurement_name,
                        "time_column_name": time_col_name,
                        "tz_data": timezone,
                        "value_column_name": val_col_name,
                        "unit": unit,
                        "apply_delta": apply_delta,
                        "repeat_data": repeat_data,
                        "regular_data": regular_data,
                        "synchronized_data": synchronized_data,
                        "interval": interval
                    }
                ],
                "remove": []
            }
        }

    def __format_table_name(self, table_name: str) -> str:
        """ Format table name to use lower case and no spaces and no special characters """
        return ''.join(chr.lower() for chr in table_name if chr.isalnum() or chr == ' ').replace(' ', '_')
