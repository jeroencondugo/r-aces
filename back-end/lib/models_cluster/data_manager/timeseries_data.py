import os
from datetime import datetime

import pandas as pd

from cdglib.database import Base, ClusterBase
from cdglib.models_domain.data_manager import TimeseriesData as DomainTimeseriesData


class TimeseriesData(ClusterBase,DomainTimeseriesData):
    __tablename__ = 'timeseries_data'
    __table_args__ = {'schema': 'clusterschema'}

    def __init__(self, database_name: str, table_name: str, column_name:str=None):
        DomainTimeseriesData.__init__(self,database_name, table_name, column_name)