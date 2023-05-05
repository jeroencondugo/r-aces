#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.models_domain.meter_configs.meter_config_historian import MeterConfigHistorianBase
from .meter_config_base import MeterConfig


class MeterConfigHistorian(MeterConfig, MeterConfigHistorianBase):
    __tablename__ = 'meter_config_historian'

    id = Column(Integer, ForeignKey('clusterschema.meter_config.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'MeterConfigHistorian', 'inherit_condition': id == MeterConfig.id}

    historian_id = Column(Integer(), ForeignKey('clusterschema.historian.id', name='meter_config_historian_historian_id_fk'))

    # relationships
    historian = relationship("Historian")
