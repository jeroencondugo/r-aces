#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref

from cdglib.database import ClusterBase
from cdglib.models_domain.basetrees.node import NodeBase

node_meter_table = Table('ass_node_meter', ClusterBase.metadata,
                         Column('meter_id', Integer, ForeignKey('clusterschema.meter.id', ondelete="CASCADE", onupdate="CASCADE"), index=True),
                         Column('node_id', Integer, ForeignKey('clusterschema.node.id', ondelete="CASCADE", onupdate="CASCADE"), index=True),
                         schema="clusterschema"
                         )


class Node(ClusterBase, NodeBase):
    __tablename__ = 'node'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_on': 'discriminator', 'polymorphic_identity': 'Node'}

    def __init__(self, name, parent=None, locked=False, label=''):
        NodeBase.__init__(self, name=name, parent=parent, locked=locked, label=label)

    @declared_attr
    def node_id(self):
        return Column(Integer, ForeignKey('clusterschema.node.id'), index=True)

    @declared_attr
    def basetree_id(self):
        return Column(Integer, ForeignKey('clusterschema.basetree.id', name="fk_site_to_hierarchy"), index=True)

    @declared_attr
    def parent(self):
        return relationship("Node", foreign_keys="[Node.node_id]", remote_side="[Node.id]", primaryjoin="Node.id==Node.node_id", backref=backref("children"))

    @declared_attr
    def meters(self):
        return relationship("Meter", secondary=node_meter_table, lazy="dynamic", backref="sites")
