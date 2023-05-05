#  Copyright (c) 2015-2021 Condugo bvba

from cdglib.models_domain.historians import SQLAHistorianBase
from .historian_base import Historian


class SQLAHistorian(Historian, SQLAHistorianBase):
    """ Config class for a relational database historian """

    __mapper_args__ = {
        "polymorphic_identity": 'SQLAHistorian'
    }
