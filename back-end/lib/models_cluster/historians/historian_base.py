#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from cdglib.database import ClusterBase
from cdglib.models_domain.historians import HistorianBase


class Historian(ClusterBase, HistorianBase):
    __tablename__ = "historian"
    __table_args__ = {"schema": "clusterschema"}
    __mapper_args__ = {"polymorphic_on": "_type", "polymorphic_identity": "Historian"}

    organisation_id = Column(Integer, ForeignKey("clusterschema.organisation.id"))

