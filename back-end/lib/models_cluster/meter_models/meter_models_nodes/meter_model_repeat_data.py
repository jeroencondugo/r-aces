from sqlalchemy import Column, ForeignKey, Integer

from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode
from cdglib.models_domain.meter_models.meter_models_nodes import MeterModelRepeatData as DomainMeterModelRepeatData

class MeterModelRepeatData(MeterModelNode,DomainMeterModelRepeatData):
    __tablename__ = 'meter_model_repeat_data'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity': 'MeterModelRepeatData'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)

    def __init__(self, name=None, graph_id: int = None, catalog_id=None):
        DomainMeterModelRepeatData.__init__(self, name, graph_id, catalog_id)
