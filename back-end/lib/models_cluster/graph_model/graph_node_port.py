#  Copyright (c) 2015-2021 Condugo bvba
from sqlalchemy import Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain import GraphNodePortBase, GraphNodePortInputBase, GraphNodePortOutputBase

ass_graphnodeinput_meter = Table('ass_graphnodeinput_meter', ClusterBase.metadata,
                                 Column('graph_node_port_input_id', Integer,
                                        ForeignKey('clusterschema.graph_node_port.id')),
                                 Column('meter_id', Integer, ForeignKey('clusterschema.meter.id')),
                                 schema="clusterschema", extend_existing=True
                                 )

ass_graphnodeoutput_meter = Table('ass_graphnodeoutput_meter', ClusterBase.metadata,
                                  Column('graph_node_port_output_id', Integer,
                                         ForeignKey('clusterschema.graph_node_port.id')),
                                  Column('meter_id', Integer, ForeignKey('clusterschema.meter.id')),
                                  schema="clusterschema", extend_existing=True
                                  )


class GraphNodePort(ClusterBase, GraphNodePortBase):
    __tablename__ = "graph_node_port"
    __table_args__ = {"schema": "clusterschema"}
    __mapper_args__ = {"polymorphic_on": "discriminator"}

    graph_node_id = Column(Integer, ForeignKey("clusterschema.graph_node.id", ondelete="CASCADE"))
    ct_id = Column(Integer, ForeignKey('clusterschema.commodity_type.id', ondelete="CASCADE"))
    ct = relationship("CommodityType", uselist=False, single_parent=True)

    numerator_ratios = relationship("Ratio", back_populates="numerator_port", primaryjoin="Ratio.numerator_port_id==GraphNodePort.id")
    denominator_ratios = relationship("Ratio", back_populates="denominator_port", primaryjoin="Ratio.denominator_port_id==GraphNodePort.id")

    ratios = relationship("Ratio", primaryjoin="or_(Ratio.numerator_port_id==GraphNodePort.id, Ratio.denominator_port_id==GraphNodePort.id)")


class GraphNodePortInput(GraphNodePort, GraphNodePortInputBase):
    """
    A graph node input port has a commodity type associated with it.
    """
    __mapper_args__ = {"polymorphic_identity": "in"}

    meters = relationship("Meter", secondary=ass_graphnodeinput_meter, backref="input_ports")


class GraphNodePortOutput(GraphNodePort, GraphNodePortOutputBase):
    """
    A graph node output port has a commodity type associated with it.
    """
    __mapper_args__ = {"polymorphic_identity": "out"}

    input_port_id = Column(Integer, ForeignKey(GraphNodePortInput.id, ondelete="SET NULL"))
    input_port = relationship("GraphNodePortInput", remote_side=GraphNodePortInput.id, primaryjoin=GraphNodePortInput.id==input_port_id)

    meters = relationship("Meter", secondary=ass_graphnodeoutput_meter, backref="output_ports")
