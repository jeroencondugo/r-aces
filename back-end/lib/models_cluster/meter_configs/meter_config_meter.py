#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_meter import MeterConfigMeterBase
from .meter_config_base import MeterConfig


class MeterConfigMeter(MeterConfig, MeterConfigMeterBase):
    __tablename__ = 'meter_config_meter'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigMeter', 'inherit_condition': id == MeterConfig.id}

    source_meter_id = Column(Integer, ForeignKey('clusterschema.meter.id'), index=True)
    source_meter = relationship("Meter", foreign_keys=[source_meter_id])
