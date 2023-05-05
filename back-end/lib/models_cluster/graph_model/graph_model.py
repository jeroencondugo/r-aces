#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain import GraphModelBase
from cdglib.models_cluster.classmap import ClassMap


class GraphModel(ClusterBase, GraphModelBase):
    __tablename__ = 'graph_model'
    __table_args__ = {'schema': 'clusterschema'}

    nodes = relationship("GraphNode", back_populates="graph_model", cascade="all, delete-orphan")

    source_nodes = relationship("GraphNodeSource")
    converter_nodes = relationship("GraphNodeConverter")
    sink_nodes = relationship("GraphNodeSink")
    distributor_nodes = relationship("GraphNodeDistributor")

    exports = relationship('GraphModelExport', cascade="delete")
