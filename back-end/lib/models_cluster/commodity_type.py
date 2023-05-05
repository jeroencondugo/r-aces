from sqlalchemy import Column, Integer, ForeignKey, Table

from cdglib.database import ClusterBase
from cdglib.models_cluster import Node
from cdglib.models_domain import CommodityTypeBase

commodity_type_meter_table = Table('ass_commodity_type_meters', ClusterBase.metadata,
                                   Column('meter_id', Integer, ForeignKey('clusterschema.meter.id')),
                                   Column('commodity_type_id', Integer, ForeignKey('clusterschema.commodity_type.id')),
                                   schema="clusterschema"
                                   )


class CommodityType(Node, CommodityTypeBase):
    __tablename__ = 'commodity_type'
    __table_args__ = {'schema': 'clusterschema'}
    __mapper_args__ = {'polymorphic_identity': 'CommodityType'}

    id = Column(Integer, ForeignKey('clusterschema.node.id'), primary_key=True)
