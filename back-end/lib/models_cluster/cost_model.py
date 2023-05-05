#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_cluster import CommodityType
from cdglib.models_domain import CostModelBase


class CostModel(ClusterBase, CostModelBase):
    __tablename__ = 'cost_model'
    __table_args__ = {'schema': 'clusterschema'}

    commodity_id = Column(Integer, ForeignKey('clusterschema.commodity_type.id', ondelete="cascade"))
    commodity_type = relationship(CommodityType, back_populates='costs')
