from datetime import datetime
from typing import List, Tuple

import pandas as pd

from cdg_service.service.common.base_service import Service
from cdg_service.service.timeseries_data.timesseries_data import TimeseriesDataService
from cdglib.init_lib import get_error_client
from cdglib.meter_type import MeterType
from cdglib.models_client import Meter
from cdglib.models_domain.data_manager.timeseries_meter_data import TimeseriesMeterData
from cdglib.utils.df_utils.df_manipulator_model import DFManipulatorModel
from cdglib.utils.df_utils.manipulations.differentiate import Differentiate, DifferentiateOptions
from cdglib.utils.df_utils.manipulations.remove_non_reals import RemoveNonReals
from cdglib.utils.df_utils.manipulations.sync_and_interpolate import SyncAndInterpolate


class MeterDataService(Service):

    # Get the absolute raw data from the database
    def read_raw(self, meter_id: int, begin: datetime = None, end: datetime = None) -> pd.DataFrame:
        begin, end = self._init_time(begin, end)
        meter_data_info: TimeseriesMeterData = self._meters_query(meter_id).first()
        return TimeseriesDataService(self.session).get_data(id=meter_data_info.timeseries_id, begin=begin, end=end)

    def get_unit(self, meter_id: int):
        try:
            meter_data_info: TimeseriesMeterData = self._meters_query(meter_id).first()
            return meter_data_info.unit
        except Exception as e:
            get_error_client().report(f"Trying to get unit from unexisting timeseriesMeterData with id {meter_id}")

    # private method
    def _read(self, meter: Meter, begin: datetime = None, end: datetime = None) -> pd.DataFrame:
        self.apply_delta = False
        try:
            df = self.read_raw(meter.id, begin, end)
            df = DFManipulatorModel([
                RemoveNonReals(0.0),
                SyncAndInterpolate(
                    interpolation_strategy=meter.measure.interpolation_strategy,
                    apply_delta=self.apply_delta,
                    frequency='15T')
            ],
            ).process(df)
            assert isinstance(df,
                              pd.DataFrame), f"{self.__class__.__name__} has not returned a pandas dataframe but a {type(df)}"
            return df
        except Exception as e:
            raise Exception(f"Error loading data! {e}")

    # Get data that is preprocessed
    # Skip virtual is only relevant for calculations in the MeterModelGraph. Else don't bother setting this variable
    def read(self, meter_id: int, begin: datetime = None, end: datetime = None,
             skip_virtual: bool = False) -> pd.DataFrame:
        meter: Meter = self.session.query(self._classmap.Meter).get(meter_id)
        if meter.meter_type == MeterType.MANUAL.value or skip_virtual:
            df = self._read(meter, begin, end)
            assert isinstance(df,
                          pd.DataFrame), f"{self.__class__.__name__}: manual meter: has not returned a pandas dataframe but a {type(df)}"
        else:
            from cdg_service.service.meter_model.meter_model_service import MeterModelService
            full_graph = MeterModelService(self.session).read_full_graph(meter_id)
            df = full_graph.get_output(begin, end)
            assert isinstance(df,
                          pd.DataFrame), f"{self.__class__.__name__}: virtual meter: has not returned a pandas dataframe but a {type(df)}"
        df = self._rename_df_column_to_val(df)
        return df

    def read_by_tablename(self, meter_id: int, table_name, measure_id, begin: datetime = None,
                          end: datetime = None):
        if table_name is None or table_name == '':
            raise Exception("Table name needs to be defined!")
        meter_data_info: List[TimeseriesMeterData] = self._meters_query(meter_id).all()

        count = [data_info for data_info in meter_data_info if data_info.table_name == table_name].__len__()
        non_existent = count <= 0 and not meter_data_info
        exists_wrong_table_name = count <= 0
        if non_existent:
            self.create_meter_data(meter_id=meter_id, table_name=table_name, measure_id=measure_id)
        if exists_wrong_table_name:
            self._update_table_name(meter_data_info[0], table_name)

        df = self.read_raw(meter_id, begin, end)
        df = self._rename_df_column_to_val(df)
        return df

    def create_meter_data(self, meter_id: int, table_name, measure_id):

        client_id = self.session.query(self._classmap.Organisation).first().client_id()
        timeseries_data = TimeseriesDataService(self.session).create(database_name=f"%ENV%-m_{client_id}",
                                                                     table_name=table_name)
        meter_data = self._classmap.TimeseriesMeterData(meter_id, table_name, timeseries_data.id)
        meter_data.measure_id = measure_id
        self.session.add(meter_data)
        self.session.flush()
        return meter_data


    def write_data(self, meter_id: int, unit: str, data):
        try:
            meter_data: TimeseriesMeterData = self.session.query(self._classmap.TimeseriesMeterData).filter(
                self._classmap.TimeseriesMeterData.meter_id == meter_id).first()
        except Exception as e:
            get_error_client().report(
                f"MeterData for meter_id: {meter_id} does not exist! Was trying to write to it")
        if not meter_data.unit:
            meter_data.unit = unit
        else:
            if meter_data.unit != unit:
                get_error_client().report(
                    f'Trying to write values with a different unit to meter_id:{meter_id} with id timeseriesData {meter_data.timeseries_id}')
        self.session.flush()
        TimeseriesDataService(self.session).write_data(meter_data.timeseries_id, data)

    def exists(self, meter_id: int):
        meter_data_infos = self._meters_query(meter_id).all()
        return meter_data_infos.__len__() >= 1

    def _rename_df_column_to_val(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Rename the df's first column to 'val' """
        columns = df.columns.tolist()
        if columns:
            columns[0] = 'val'
            df.columns = columns
        return df

    def get_extent(self, meter_id:int)->Tuple[datetime, datetime]:
        meter = self.session.query(self._classmap.Meter).get(meter_id)
        if(meter.meter_type == MeterType.MANUAL.value):
            meter_data_infos: List[TimeseriesMeterData] = self._meters_query(meter_id).all()
            if meter_data_infos.__len__() > 1:
                raise Exception(f"Multiple sources found for meter {meter_id}! Please define a table_name!")
            meter_data = meter_data_infos[0]
            return TimeseriesDataService(self.session).get_extent(id=meter_data.timeseries_id)
        else:
            from cdg_service.service.meter_model.meter_model_service import MeterModelService
            full_graph = MeterModelService(self.session).read_full_graph(meter_id)
            extent = full_graph.get_extent()
        return extent

    def get_database_extent(self, meter_id:int, table_name, measure_id):
        if table_name is None or table_name == '':
            raise Exception("Table name needs to be defined!")
        meter_data_info: List[TimeseriesMeterData] = self._meters_query(meter_id).all()
        count = [data_info for data_info in meter_data_info if data_info.table_name == table_name].__len__()
        if count <= 0:
            timeseries_meter_data = self.create_meter_data(meter_id=meter_id, table_name=table_name, measure_id=measure_id)
        else:
            timeseries_meter_data= meter_data_info[0]

        return TimeseriesDataService(self.session).get_extent(id=timeseries_meter_data.timeseries_id)

    def _init_time(self, begin, end):
        if not begin:
            begin = datetime(1970, 2, 1)
        if not end:
            end = datetime(2200, 1, 1)
        return begin, end

    def _meters_query(self, meter_id, table_name=None):
        if table_name:
            return self.session.query(self._classmap.TimeseriesMeterData).filter(
                self._classmap.TimeseriesMeterData.meter_id == meter_id,
                self._classmap.TimeseriesMeterData.table_name == table_name)
        else:
            return self.session.query(self._classmap.TimeseriesMeterData).filter(self._classmap.TimeseriesMeterData.meter_id == meter_id)

    def _update_table_name(self, meter_data_info:TimeseriesMeterData, table_name):
        meter_data_info.table_name = table_name
        TimeseriesDataService(self.session).update_table_name(meter_data_info.timeseries_id, table_name)

    def update_table_name(self, meter_id, table_name):
        meter_data_info = self._meters_query(meter_id).first()
        if meter_data_info.table_name != table_name:
            self._update_table_name(meter_data_info, table_name)

    def delete(self, meter_id: int):
        """ Delete timeseries meter data object with meter_data_id """
        TimeseriesMeterData = self._classmap.TimeseriesMeterData
        TimeseriesData = self._classmap.TimeseriesData
        meter_datas = self.session.query(TimeseriesMeterData).filter(TimeseriesMeterData.meter_id == meter_id).all()
        for meter_data in meter_datas:
            ts_data = self.session.query(TimeseriesData).filter(TimeseriesData.id == meter_data.timeseries_id).first()
            self.session.delete(meter_data)
            self.session.flush()
            if ts_data:
                self.session.delete(ts_data)
                self.session.flush()
