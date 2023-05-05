#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_constant import MeterConfigConstantBase
from .meter_config_base import MeterConfig


class MeterConfigConstant(MeterConfig, MeterConfigConstantBase):
    __tablename__ = 'meter_config_constant'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigConstant' , 'inherit_condition': id == MeterConfig.id}

    constant_id = Column(Integer, ForeignKey('clusterschema.constant.id', ondelete="SET NULL"), index=True)
    constant = relationship("Constant", uselist=False)
