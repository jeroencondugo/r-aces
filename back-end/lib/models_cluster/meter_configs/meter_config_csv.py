#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey

from cdglib.models_domain.meter_configs.meter_config_csv import MeterConfigCSVBase
from .meter_config_base import MeterConfig


class MeterConfigCSV(MeterConfig, MeterConfigCSVBase):
    __tablename__ = 'meter_config_csv'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigCSV', 'inherit_condition': id == MeterConfig.id}
