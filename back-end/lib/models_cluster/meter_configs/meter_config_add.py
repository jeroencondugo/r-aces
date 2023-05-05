#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_add import MeterConfigAddBase
from .meter_config_base import MeterConfig


class MeterConfigAdd(MeterConfig, MeterConfigAddBase):
    __tablename__ = 'meter_config_add'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigAdd', 'inherit_condition': id == MeterConfig.id}

    port_a_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_b_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_c_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_d_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_e_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))

    port_a = relationship("MeterConfig", foreign_keys=[port_a_id])
    port_b = relationship("MeterConfig", foreign_keys=[port_b_id])
    port_c = relationship("MeterConfig", foreign_keys=[port_c_id])
    port_d = relationship("MeterConfig", foreign_keys=[port_d_id])
    port_e = relationship("MeterConfig", foreign_keys=[port_e_id])
