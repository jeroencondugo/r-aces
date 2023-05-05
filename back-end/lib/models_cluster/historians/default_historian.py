#  Copyright (c) 2015-2021 Condugo bvba

from cdglib.models_domain.historians import DefaultHistorianBase
from .historian_base import Historian


class DefaultHistorian(Historian, DefaultHistorianBase):
    """ This historian will be the default historian for each client to store meter information in influxdb.
    The influx server properties can be found in the config. The measurement database is called m_<client_id> and
    the username and password are in the config and also in the domain class in the general schema. """

    __mapper_args__ = {
        'polymorphic_identity': 'DefaultHistorian'
    }
