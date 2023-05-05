#  Copyright (c) 2015-2021 Condugo bvba

from cdglib.database import ClusterBase

from cdglib.models_domain.meter_models.meter_models_nodes.meter_model_node import \
    MeterModelNode as DomainMeterModelNode, MeterModelNodeType


class MeterModelNode(ClusterBase, DomainMeterModelNode):
    __tablename__ = 'meter_model_node'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_on':'node_discriminator',
        'polymorphic_identity':'MeterModelNode'
    }
    """ Meter config base class """


    def __init__(self, name: str, discriminator:str, graph_id:int,node_type=MeterModelNodeType.NORMAL, catalog_id=None):
        DomainMeterModelNode.__init__(self, name, discriminator, graph_id, node_type, catalog_id)

