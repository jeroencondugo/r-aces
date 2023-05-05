#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey

from cdglib.models_cluster.basetrees.node import Node
from cdglib.models_domain import ProductBase


class Product(Node, ProductBase):
    __tablename__ = 'product'
    __table_args__ = {'schema' : 'clusterschema'}
    __mapper_args__ = {'polymorphic_on': 'discriminator', 'polymorphic_identity': 'Product'}

    id = Column(Integer, ForeignKey('clusterschema.node.id'), primary_key=True)

    def __init__(self, name, parent=None, locked=False, label=''):
        super().__init__(name, parent, locked=locked, label=label)
