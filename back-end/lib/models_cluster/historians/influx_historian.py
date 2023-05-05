#  Copyright (c) 2015-2021 Condugo bvba

from cdglib.models_domain.historians import InfluxHistorianBase
from .historian_base import Historian


class InfluxHistorian(Historian, InfluxHistorianBase):
    """ Config class for an influxdb historian """

    __mapper_args__ = {
        'polymorphic_identity': 'InfluxHistorian'
    }
