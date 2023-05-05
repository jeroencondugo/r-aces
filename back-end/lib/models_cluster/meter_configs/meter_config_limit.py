#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_limit import MeterConfigLimitBase
from .meter_config_base import MeterConfig


class MeterConfigLimit(MeterConfig, MeterConfigLimitBase):
    __tablename__ = 'meter_config_limit'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigLimit', 'inherit_condition': id == MeterConfig.id}

    port_in_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"))
    port_in = relationship("MeterConfig", foreign_keys=[port_in_id])
