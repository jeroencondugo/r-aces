from cdglib.database import Base, ClusterBase

from sqlalchemy import Column, Integer, String,ForeignKey

from cdglib.models_domain.meter_models import MeterModelEdge as DomainMeterModelEdge


class MeterModelEdge(ClusterBase,DomainMeterModelEdge):
    __tablename__ = 'meter_model_edge'
    __table_args__ = {'schema': 'clusterschema'}

    start_node_id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete='cascade'))
    end_node_id = Column(Integer,ForeignKey('clusterschema.meter_model_node.id', ondelete='cascade'))

    def __init__(self,
                 graph_id:int,
                 start_node_id:int=None,
                 end_node_id: int=None,
                 start_port_id:str=None,
                 end_port_id:str=None,
                 start_port_name:str=None,
                 end_port_name:str=None,
                 end_port_measure_id:int=None,
                 start_port_measure_id:int=None):
        DomainMeterModelEdge.__init__(self,graph_id, start_node_id, end_node_id,start_port_id, start_port_name, end_port_name, end_port_measure_id, start_port_measure_id)