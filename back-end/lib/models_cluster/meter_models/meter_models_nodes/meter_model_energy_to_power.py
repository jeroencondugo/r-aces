from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode

from sqlalchemy import Column, ForeignKey, Integer

from cdglib.models_domain.meter_models.meter_models_nodes import \
    MeterModelEnergyToPower as DomainMeterModelEnergyToPower


class MeterModelEnergyToPower(MeterModelNode,DomainMeterModelEnergyToPower):
    __tablename__ = 'meter_model_energy_to_power'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity': 'MeterModelEnergyToPower'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)
    def __init__(self, name=None, graph_id: int = None, catalog_id=None):
        DomainMeterModelEnergyToPower.__init__(self, name, graph_id, catalog_id)