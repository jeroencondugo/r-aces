import os
from datetime import datetime

from cdglib import MeasureRegister
from cdglib.database import Base, ClusterBase
from cdglib.init_lib import logger
from sqlalchemy import Column, Integer, String, ForeignKey
from cdglib.influx import influx_manager as influxManager
from sqlalchemy.orm import relationship

from cdglib.models_domain.data_manager import TimeseriesMeterData as DomainTimeseriesMeterData


class TimeseriesMeterData(ClusterBase,DomainTimeseriesMeterData):
    __tablename__ = 'timeseries_meter_data'
    __table_args__ = {'schema': 'clusterschema'}



    def __init__(self, meter_id: int, table_name: str, timeseries_id:int):
        DomainTimeseriesMeterData.__init__(self,meter_id, table_name, timeseries_id)
