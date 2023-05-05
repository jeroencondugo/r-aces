from sqlalchemy import Integer, ForeignKey, Column

from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode
from cdglib.models_domain.meter_models.meter_models_nodes import MeterModelTankConsumption as DomainMeterModelTankConsumption


class MeterModelTankConsumption(MeterModelNode,DomainMeterModelTankConsumption):

    __tablename__ = 'meter_model_tank_consumption'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity':'MeterModelTankConsumption'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)



    def __init__(self,name=None,graph_id:int=None, catalog_id=None):
        DomainMeterModelTankConsumption.__init__(self, name, graph_id, catalog_id)