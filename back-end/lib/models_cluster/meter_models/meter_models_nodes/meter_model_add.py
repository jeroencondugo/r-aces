from sqlalchemy import Integer, ForeignKey, Column

from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode
from cdglib.models_domain.meter_models.meter_models_nodes import MeterModelAdd as DomainMeterModelAdd


class MeterModelAdd(MeterModelNode,DomainMeterModelAdd):

    __tablename__ = 'meter_model_add'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity':'MeterModelAdd'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)


    def __init__(self,name=None,graph_id:int=None, catalog_id=None):
        DomainMeterModelAdd.__init__(self, name, graph_id, catalog_id)
