#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain.meter_configs.meter_config_base import MeterConfigBase


class MeterConfig(ClusterBase, MeterConfigBase):
    """ Meter config base class """
    # -----------------------------------------------------------------------
    # SqlAlchemy schema definition

    __tablename__ = 'meter_config'
    __mapper_args__ = {'polymorphic_on': "discriminator"}

    @declared_attr
    def __table_args__(self):
        return {'schema': 'clusterschema'}

    # -----------------------------------------------------------------------
    # Columns

    meter_id = Column(Integer, ForeignKey('clusterschema.meter.id', ondelete="CASCADE"), index=True)

    # -----------------------------------------------------------------------
    # Relationships

    # importers = relationship("MeasurementImporter", lazy="dynamic", backref="config")

    def __init__(self, name: str = "Meter config"):
        MeterConfigBase.__init__(self, name=name)
