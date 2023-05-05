#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, backref

from cdglib.database import ClusterBase
from cdglib.models_cluster.basetrees.node import Node
from cdglib.models_cluster.classmap import ClassMap
from cdglib.models_cluster.commodity_type import CommodityType
from cdglib.models_domain import GraphNodeBase, GraphNodeConverterBase, GraphNodeSourceBase, GraphNodeDistributorBase, \
    GraphNodeSinkBase

ass_graphnode_site = Table('ass_graphnode_node', ClusterBase.metadata,
    Column('graph_node_id', Integer, ForeignKey('clusterschema.graph_node.id'), primary_key=True),
    Column('site_id', Integer, ForeignKey('clusterschema.node.id'), primary_key=True),
    schema="clusterschema"
)


class GraphNode(ClusterBase, GraphNodeBase):
    __tablename__ = 'graph_node'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_on': 'discriminator'}

    client_id = Column(Integer, default=None, index=True)
    graph_model_id = Column(Integer, ForeignKey('clusterschema.graph_model.id', ondelete="CASCADE"))
    graph_model = relationship("GraphModel", back_populates="nodes")

    input_ports = relationship("GraphNodePortInput", uselist=True, backref='graph_node',
                               cascade="save-update, merge, delete")
    output_ports = relationship("GraphNodePortOutput", uselist=True, backref='graph_node',
                                cascade="save-update, merge, delete")

    site = relationship("Node", secondary=ass_graphnode_site, uselist=False)
    building_or_room_id = Column(Integer, ForeignKey('clusterschema.node.id'))
    building_or_room = relationship("Node", foreign_keys=[building_or_room_id])
    grouping_id = Column(Integer, ForeignKey('clusterschema.node.id', ondelete="SET NULL"), index=True)
    grouping = relationship("Node", foreign_keys=[grouping_id], backref=backref("graphnodes"))

    def register_site(self, site: Node):
        if isinstance(site, Node):
            self.site = site


class GraphNodeConverter(GraphNode, GraphNodeConverterBase):
    """
    A converter graph node is a graph node with multiple inputs and multiple outputs. Each connection is of one commodity type.
    """
    __tablename__ = 'graph_node_converter'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_identity': 'GraphNodeConverter'}

    id = Column(Integer, ForeignKey('clusterschema.graph_node.id', ondelete="CASCADE"), primary_key=True)
    ratios = relationship("Ratio", back_populates="node", cascade="all, delete-orphan")


class GraphNodeSource(GraphNode, GraphNodeSourceBase):
    """
    A source graph node is a graph node with a single output of one commodity type.
    """
    __tablename__ = 'graph_node_source'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_identity': 'GraphNodeSource'}

    id = Column(Integer, ForeignKey('clusterschema.graph_node.id', ondelete="CASCADE"), primary_key=True)


class GraphNodeDistributor(GraphNode, GraphNodeDistributorBase):
    """
    A converter distributor graph node is a graph node with a single input and multiple outputs. All connections are of one commodity type. Output connections
    are only allowed to converter graph nodes or customer distributor graph nodes. Input connections can come from sources or converters.
    """
    __tablename__ = 'graph_node_distributor'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_identity': 'GraphNodeDistributor'}

    id = Column(Integer, ForeignKey('clusterschema.graph_node.id', ondelete="CASCADE"), primary_key=True)
    commodity_type_id = Column(Integer, ForeignKey('clusterschema.commodity_type.id', ondelete="CASCADE"))
    commodity_type = relationship(CommodityType)


class GraphNodeSink(GraphNode, GraphNodeSinkBase):
    """
    A sink graph node is a graph node with multiple inputs and no outputs. Each connection is of one commodity type. Each input can only come from customer
    distributor graph nodes of the same commodity type.
    """
    __tablename__ = 'graph_node_sink'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_identity': 'GraphNodeSink'}

    id = Column(Integer, ForeignKey('clusterschema.graph_node.id', ondelete="CASCADE"), primary_key=True)
