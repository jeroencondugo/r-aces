#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey

from cdglib.models_cluster.basetrees.node import Node
from cdglib.models_domain.basetrees.production_line import ProductionLineBase


class ProductionLine(Node, ProductionLineBase):
    __tablename__ = 'production_line'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_identity': 'ProductionLine'}

    id = Column(Integer, ForeignKey('clusterschema.node.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, name, parent=None, locked=False, label=''):
        super().__init__(name, parent, locked=locked, label=label)
