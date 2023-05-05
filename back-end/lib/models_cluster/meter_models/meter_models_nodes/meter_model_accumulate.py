from sqlalchemy import Column, ForeignKey, Integer

from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode
from cdglib.models_domain.meter_models.meter_models_nodes import MeterModelAccumulate as DomainMeterModelAccumulate


class MeterModelAccumulate(MeterModelNode,DomainMeterModelAccumulate):
    __tablename__ = 'meter_model_accumulate'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity': 'MeterModelAccumulate'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)

    def __init__(self, name=None, graph_id: int = None, catalog_id=None):
        DomainMeterModelAccumulate.__init__(self, name, graph_id, catalog_id)
