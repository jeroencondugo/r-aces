#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_binary_operator import MeterConfigBinaryOperatorBase
from .meter_config_base import MeterConfig


class MeterConfigBinaryOperator(MeterConfig, MeterConfigBinaryOperatorBase):
    __tablename__ = 'meter_config_binary_operator'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigBinaryOperator', 'inherit_condition': id == MeterConfig.id}

    port_left_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_right_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))

    port_left = relationship("MeterConfig", foreign_keys=[port_left_id])
    port_right = relationship("MeterConfig", foreign_keys=[port_right_id])
