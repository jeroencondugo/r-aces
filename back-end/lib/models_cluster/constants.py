#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from cdglib.database import ClusterBase
from cdglib.models_domain import ConstantBase


class Constant(ClusterBase, ConstantBase):
    """
    Represents a constant, which can defines a named constant value with a description
    and a unit.
    """

    # -----------------------------------------------------------------------
    # SqlAlchemy schema definition

    __tablename__ = 'constant'
    __table_args__ = {'schema': 'clusterschema'}

    # -----------------------------------------------------------------------
    # Columns

    organisation_id = Column(Integer, ForeignKey('clusterschema.organisation.id'))

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------
    commodity_type_id = Column(Integer, ForeignKey('clusterschema.commodity_type.id'))
    commodity_type = relationship("CommodityType", uselist=False)

    # -----------------------------------------------------------------------
    # Public methods

    def __init__(self, magnitude: float, unit: str, name: str = "", description: str = "", commodity_type_id: int = None):
        ConstantBase.__init__(self, magnitude=magnitude, unit=unit, name=name, description=description, commodity_type_id=commodity_type_id)
