from cdglib.database import ClusterBase
from cdglib.models_domain import GraphNodeReportBase


class GraphNodeReport(ClusterBase, GraphNodeReportBase):
    __tablename__ = 'graph_node_report'
    __table_args__ = {'schema': 'clusterschema'}
