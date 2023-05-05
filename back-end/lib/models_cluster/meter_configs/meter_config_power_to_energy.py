#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_power_to_energy import MeterConfigPowerToEnergyBase
from .meter_config_base import MeterConfig


class MeterConfigPowerToEnergy(MeterConfig, MeterConfigPowerToEnergyBase):
    __tablename__ = 'meter_config_power_to_energy'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigPowerToEnergy', 'inherit_condition': id == MeterConfig.id}

    port_in_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_in = relationship("MeterConfig", foreign_keys=[port_in_id])
