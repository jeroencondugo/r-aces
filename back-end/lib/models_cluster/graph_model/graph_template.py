from sqlalchemy import Integer, Column, ForeignKey, Table
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain import GraphTemplateBase

ass_graphnode_template = Table('ass_graph_node_template', ClusterBase.metadata,
    Column('node_id', Integer, ForeignKey('clusterschema.graph_node.id', ondelete='cascade'), primary_key=True),
    Column('template_id', Integer, ForeignKey('clusterschema.graph_template.id', ondelete='cascade'), primary_key=True),
    schema="clusterschema"
)


class GraphTemplate(ClusterBase, GraphTemplateBase):
    __tablename__ = 'graph_template'
    __table_args__ = {'schema': 'clusterschema'}

    graph_node_ids = relationship("GraphNode", secondary=ass_graphnode_template, lazy="dynamic", backref='graph_template')
