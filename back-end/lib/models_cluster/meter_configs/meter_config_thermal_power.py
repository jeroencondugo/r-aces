#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_thermal_power import MeterConfigThermalPowerBase
from .meter_config_base import MeterConfig


class MeterConfigThermalPower(MeterConfig, MeterConfigThermalPowerBase):
    __tablename__ = 'meter_config_thermal_power'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigThermalPower', 'inherit_condition': id == MeterConfig.id}

    density_constant_id = Column(Integer, ForeignKey('clusterschema.constant.id', ondelete="SET NULL"), index=True)
    density_constant = relationship("Constant", uselist=False, foreign_keys=[density_constant_id])

    heat_capacity_constant_id = Column(Integer, ForeignKey('clusterschema.constant.id', ondelete="SET NULL"), index=True)
    heat_capacity_constant = relationship("Constant", uselist=False, foreign_keys=[heat_capacity_constant_id])

    port_tin_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_tout_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_flow_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))

    port_tin = relationship("MeterConfig", foreign_keys=[port_tin_id])
    port_tout = relationship("MeterConfig", foreign_keys=[port_tout_id])
    port_flow = relationship("MeterConfig", foreign_keys=[port_flow_id])
