#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain.meter import MeterBase


write_config_table = Table('ass_write_config', ClusterBase.metadata,
                           Column('meter_id', Integer, ForeignKey('clusterschema.meter.id'), primary_key=True, index=True),
                           Column('config_id', Integer, ForeignKey('clusterschema.meter_config.id'), index=True),
                           schema="clusterschema"
                           )


class Meter(ClusterBase, MeterBase):
    """
    Represents a meter, which can provide measurements.
    Each meter belongs to a maximum of one commodity type PER SITE HIERARCHY.
    Similarly, each meter belongs to a maximum of one site PER SITE HIERARCHY.
    """

    # -----------------------------------------------------------------------
    # SqlAlchemy schema definition

    __tablename__ = 'meter'
    __table_args__ = {'schema': 'clusterschema'}

    # -----------------------------------------------------------------------
    # Columns

    organisation_id = Column(Integer, ForeignKey('clusterschema.organisation.id'), index=True)
    # sparkline_id = Column(Integer, ForeignKey('clusterschema.measurement.id'), index=True)
    source_config_id = Column(Integer, ForeignKey('clusterschema.meter_config.id', ondelete="SET NULL"), index=True)

    # -----------------------------------------------------------------------
    # Relationships

    # meters
    # NOTE: alarm_traps defined as backref in AlarmTrap table
    # NOTE: alarms defined as backref in Alarm table
    source_config = relationship("MeterConfig", backref=backref("output_meter", uselist=False), foreign_keys='Meter.source_config_id', post_update=True)
    configs = relationship("MeterConfig", backref="meter", foreign_keys='MeterConfig.meter_id', lazy='joined')
    write_config = relationship('MeterConfig', secondary=write_config_table, uselist=False)

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # Public methods

    def __init__(self, name, category, measure):
        MeterBase.__init__(self, name=name, measure=measure)
