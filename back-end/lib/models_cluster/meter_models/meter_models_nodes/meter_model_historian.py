from sqlalchemy import ForeignKey, Integer, Column

from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode
from cdglib.models_domain.meter_models.meter_models_nodes import MeterModelHistorian as DomainMeterModelHistorian


class MeterModelHistorian(MeterModelNode,DomainMeterModelHistorian):


    __tablename__ = 'meter_model_historian'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity':'MeterModelHistorian'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)



    def __init__(self, name:str,graph_id: int, catalog_id=None):
        DomainMeterModelHistorian.__init__(self,name, graph_id, catalog_id)