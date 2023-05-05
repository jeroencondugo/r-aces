#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from cdglib.database import ClusterBase
from cdglib.models_domain.basetrees import NodeLevelBase


class NodeLevel(ClusterBase, NodeLevelBase):
    __tablename__ = 'node_level'
    __table_args__ = {'schema': 'clusterschema'}

    @declared_attr
    def basetree_id(self):
        return Column(Integer, ForeignKey('clusterschema.basetree.id', name="fk_level_to_hierarchy", ondelete="CASCADE"), index=True)

    def __init__(self, depth, name, color="#000000", locked=False, type=None):
        NodeLevelBase.__init__(self, depth=depth, name=name, color=color, locked=locked, type=type)
