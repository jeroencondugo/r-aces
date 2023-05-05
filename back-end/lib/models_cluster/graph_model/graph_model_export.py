#  Copyright (c) 2015-2021 Condugo bvba
from sqlalchemy import Column, Integer, ForeignKey

from cdglib.database import ClusterBase
from cdglib.models_domain import GraphModelExportBase


class GraphModelExport(ClusterBase, GraphModelExportBase):
    __tablename__ = 'graph_model_export'
    __table_args__ = {'schema': 'clusterschema'}

    graph_model_id = Column(Integer, ForeignKey('clusterschema.graph_model.id', ondelete="cascade"))  # only one measurement
