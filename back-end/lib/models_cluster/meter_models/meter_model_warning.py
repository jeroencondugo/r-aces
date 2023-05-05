from enum import Enum

from sqlalchemy import Column, Integer, ForeignKey, String
from cdglib.database import Base, ClusterBase
from cdglib.models_domain.meter_models.meter_model_warning import MeterModelWarningsType, MeterModelWarning as DomainMeterModelWarning


class MeterModelWarning(ClusterBase, DomainMeterModelWarning):
    '''
    Defines the link between the graphs and the meters.
    '''
    __tablename__ = 'meter_model_warning'
    __table_args__ = {'schema': 'clusterschema'}

    node_id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"))


    def __init__(self, node_id:int, message:str, type:str):
        DomainMeterModelWarning.__init__(self, node_id, message, type)
