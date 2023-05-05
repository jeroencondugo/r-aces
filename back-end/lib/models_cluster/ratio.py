from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain import RatioBase


class Ratio(ClusterBase, RatioBase):
    __tablename__ = "graph_node_converter_ratio"
    __table_args__ = {"schema": "clusterschema"}

    node_id = Column(Integer, ForeignKey("clusterschema.graph_node_converter.id", ondelete="CASCADE"))
    node = relationship("GraphNodeConverter", back_populates="ratios")

    numerator_port_id = Column(Integer, ForeignKey("clusterschema.graph_node_port.id", ondelete="CASCADE"))
    numerator_port = relationship("GraphNodePort", back_populates="numerator_ratios", primaryjoin="Ratio.numerator_port_id==GraphNodePort.id")

    denominator_port_id = Column(Integer, ForeignKey("clusterschema.graph_node_port.id", ondelete="CASCADE"))
    denominator_port = relationship("GraphNodePort", back_populates="denominator_ratios", primaryjoin="Ratio.denominator_port_id==GraphNodePort.id")
