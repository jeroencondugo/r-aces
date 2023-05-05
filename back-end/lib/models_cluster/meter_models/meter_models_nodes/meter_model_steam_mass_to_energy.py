from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode

from sqlalchemy import Column, ForeignKey, Integer

from cdglib.models_domain.meter_models.meter_models_nodes import \
    MeterModelSteamMassToEnergy as DomainMeterModelSteamMassToEnergy


class MeterModelSteamMassToEnergy(MeterModelNode,DomainMeterModelSteamMassToEnergy):
    __tablename__ = 'meter_model_steam_mass_to_energy'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {
        'polymorphic_identity': 'MeterModelSteamMassToEnergy'
    }

    id = Column(Integer, ForeignKey('clusterschema.meter_model_node.id', ondelete="cascade"), primary_key=True)


    def __init__(self, name=None, graph_id: int = None, catalog_id=None):
        DomainMeterModelSteamMassToEnergy.__init__(self,name, graph_id, catalog_id)