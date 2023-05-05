from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from abc import abstractmethod

import numpy as np
import pandas as pd

from cdg_service.service.common.base_service import Service
from cdglib.influx.df_influxdb import DataframeInfluxdb
from cdglib.measure import MeasureCategory
from cdglib.models_domain.graph_model.graph_model_common_dataclasses import AmountTrendValue
from cdglib.models_domain.graph_model.graph_model_link_dataclasses import LinkV2
from cdglib.period import Period


@dataclass
class DataframeValues:
    value: Optional[float] = None
    value_pp: Optional[float] = None
    value_py: Optional[float] = None


class SankeySerializationBaseService(Service):

    def __init__(self, session=None, config=None):
        super().__init__(session=session, config=config)
        self.ct_per_id = {}

    @abstractmethod
    def serialize_site(self, client_schema: str, site_id: int, period: str, start_date: datetime, end_date: datetime,
                       debug=False):
        """ Serialize the graph model on a single site """
        pass

    @abstractmethod
    def serialize_node(self, client_schema: str, site_id: int, node_id: int, period: str, start_date: datetime,
                       end_date: datetime, mc: MeasureCategory = MeasureCategory.USAGE):
        """ Serialize the graph model on a single graph node with detailed time series """
        pass

    @abstractmethod
    def serialize_config(self):
        """ Serialize the sankey config """
        pass

    @abstractmethod
    def _create_graph_model_report(self):
        """ Create a graph model report """
        pass

    @abstractmethod
    def _fetch_metadata(self, site_id: int, client_schema: str) -> bool:
        """ Fetch the graph model metadata """
        pass

    @abstractmethod
    def _fetch_time_series_data(self, client_schema: str, period: Period, start_date: datetime, end_date: datetime):
        """ Fetch the time series data """
        pass

    @abstractmethod
    def _build_links(self, df: pd.DataFrame, client_schema: str = "", site_id: Optional[int] = None,
                     period: str = "",
                     start_date_iso: str = "", debug: bool = False):
        """Add links to the serialization"""
        pass

    @abstractmethod
    def _build_nodes(self, df, df_ratios, df_dists, links: Optional[List[LinkV2]], client_schema: str, site_id: int,
                     node_id: Optional[int] = None, debug: bool = False):
        """ Build the nodes serialization """
        pass

    def create(self, sankey_serialization_dict):
        """ Method to create an sankey_serialization object """
        raise NotImplementedError

    def read(self):
        """ Method to read sankey_serialization objects """
        raise NotImplementedError

    def update(self, sankey_serialization_changes):
        """ Method to edit an sankey_serialization object """
        raise NotImplementedError

    def delete(self, sankey_serialization_id):
        """ Method to delete an sankey_serialization object """
        raise NotImplementedError

    def index(self, sankey_serialization_id):
        """ Method to index an sankey_serialization object """
        raise NotImplementedError

    def _fetch_link_values(self, df_client: DataframeInfluxdb, bucket_name: str, graph_model_id: int, period: Period,
                           start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """ Fetch link values from database """
        meaurement_name = f"gm-{graph_model_id}-meters"
        try:
            df = df_client.read(
                bucket_name=bucket_name,
                measurements=meaurement_name,
                fields=[],
                start=start_date,
                stop=end_date,
                make_index_tz_naive=True,
                include_previous_period=True,
                include_previous_year=True,
                period=period,
                reindex=True,
                tz='Europe/Brussels'
            )
        except Exception as e:
            df = None
        if df is not None: df.replace({np.nan: None}, inplace=True)
        return df

    def _fetch_ratio_values(self, df_client: DataframeInfluxdb, bucket_name: str, graph_model_id: int, period: Period,
                            start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """ Fetch link values from database """
        meaurement_name = f"gm-{graph_model_id}-ratios"
        try:
            df = df_client.read(
                bucket_name=bucket_name,
                measurements=meaurement_name,
                fields=[],
                start=start_date,
                stop=end_date,
                make_index_tz_naive=True,
                include_previous_period=True,
                include_previous_year=True,
                period=period,
                reindex=True,
                tz='Europe/Brussels'
            )
        except Exception as e:
            df = None
        return df

    def _fetch_dist_values(self, df_client: DataframeInfluxdb, bucket_name: str, graph_model_id: int, period: Period,
                           start_date: datetime, end_date: datetime,
                           fields_to_load: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
        """ Fetch link values from database """
        if fields_to_load is None:
            fields_to_load = []
        meaurement_name = f"gm-{graph_model_id}-dists"
        try:
            df = df_client.read(
                bucket_name=bucket_name,
                measurements=meaurement_name,
                fields=fields_to_load,
                start=start_date,
                stop=end_date,
                make_index_tz_naive=True,
                include_previous_period=True,
                include_previous_year=True,
                period=period,
                reindex=True,
                tz='Europe/Brussels'
            )
        except Exception as e:
            df = None
        return df

    def _get_amount_trend_value(self, link_id, measure, value, prev_period_value=None,
                                prev_year_value=None) -> AmountTrendValue:
        """ get the amount"""
        messages = []
        if value and value < 0.0:
            messages.append(
                f"Link ({link_id}) with dimension {measure.dimensionality} has negative usage value ({value}). Set to zero.")
            value = 0.0
        if prev_period_value and prev_period_value < 0.0:
            messages.append(
                f"Link ({link_id}) with dimension {measure.dimensionality} has negative usage previous period value ({prev_period_value}). Set to zero.")
            prev_period_value = 0.0
        if prev_year_value and prev_year_value < 0.0:
            messages.append(
                f"Link ({link_id}) with dimension {measure.dimensionality} has negative usage previous year value ({prev_year_value}). Set to zero.")
            prev_year_value = 0.0
        prev_period_trend = None
        if value and prev_period_value and prev_period_value != 0.0:
            prev_period_trend = (value - prev_period_value) / prev_period_value
        prev_year_trend = None
        if value and prev_year_value and prev_year_value != 0.0:
            prev_year_trend = (value - prev_year_value) / prev_year_value
        atv = AmountTrendValue(
            dimensionality=measure.dimensionality,
            value=value,
            unit=measure.unit,
            # TODO: Fix latex unit
            unit_lx=measure.unit,
            prev_period_trend=prev_period_trend,
            prev_year_trend=prev_year_trend,
            prev_period_value=prev_period_value,
            prev_year_value=prev_year_value
        )
        return atv, messages

    def _get_values_from_df(self, df, mmi, ct, debug=False):
        """ Get values from dataframe """
        usage = DataframeValues()
        energy = DataframeValues()
        column_name = mmi.influx_mapping.field_name if mmi.influx_mapping else None
        if not column_name:
            return usage, energy
        try:
            usage.value = float(df.at["main", column_name])
            if usage.value and ct and ct.is_energy:
                energy.value = usage.value * ct.default_usage_to_energy_factor
            else:
                energy.value = None
        except (KeyError, TypeError):
            usage.value = None
            energy.value = None
        try:
            usage.value_pp = float(df.at["pp", column_name])
            if usage.value_pp and ct and ct.is_energy:
                energy.value_pp = usage.value_pp * ct.default_usage_to_energy_factor
            else:
                energy.value_pp = None
        except (KeyError, TypeError):
            usage.value_pp = None
            energy.value_pp = None
        try:
            usage.value_py = float(df.at["py", column_name])
            if usage.value_py and ct and ct.is_energy:
                energy.value_py = usage.value_py * ct.default_usage_to_energy_factor
            else:
                energy.value_py = None
        except (KeyError, TypeError):
            usage.value_py = None
            energy.value_py = None
        return usage, energy

class NodeReportNotFound(Exception):
    """ Exception for when there is not node report in the db """
    pass
