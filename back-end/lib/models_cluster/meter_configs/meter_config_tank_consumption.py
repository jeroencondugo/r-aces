#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_tank_consumption import MeterConfigTankConsumptionBase
from .meter_config_base import MeterConfig


class MeterConfigTankConsumption(MeterConfig, MeterConfigTankConsumptionBase):
    __tablename__ = 'meter_config_tank_consumption'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigTankConsumption', 'inherit_condition': id == MeterConfig.id}

    port_level_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_flow_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))

    port_level = relationship("MeterConfig", foreign_keys=[port_level_id])
    port_flow = relationship("MeterConfig", foreign_keys=[port_flow_id])
