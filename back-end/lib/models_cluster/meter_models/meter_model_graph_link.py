
from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP
from sqlalchemy.orm import relationship
from cdglib.database import Base, ClusterBase
from cdglib.models_domain.meter_models import MeterModelGraphLink as DomainMeterModelGraphLink


class MeterModelGraphLink(ClusterBase, DomainMeterModelGraphLink):
    '''
    Defines the link between the graphs and the meters.
    '''
    __tablename__ = 'meter_model_graph_link'
    __table_args__ = {'schema': 'clusterschema'}
    meter_id = Column(Integer,  ForeignKey('clusterschema.meter.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, index=True, nullable=False)
    meter = relationship("Meter", foreign_keys=[meter_id])


    def __init__(self):
        DomainMeterModelGraphLink.__init__(self)