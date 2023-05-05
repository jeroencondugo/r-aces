#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy.orm import relationship
# from sqlalchemy.ext.associationproxy import association_proxy

from cdglib.database import ClusterBase
# from cdglib.models_client.organisation_settings import OrganisationSetting
from cdglib.models_cluster.historians.historian_base import Historian
from cdglib.models_domain.organisation import OrganisationBase


class Organisation(ClusterBase, OrganisationBase):
    __tablename__ = 'organisation'
    __table_args__ = {'schema': 'clusterschema'}

    def __init__(self, name, schema, base_path=None):
        OrganisationBase.__init__(self, name, schema, base_path)

    # meters = relationship("Meter", lazy="dynamic", backref="organisation")
    site_hierarchies = relationship("Basetree", lazy="dynamic", backref="organisation")

    # insights = relationship("Insight", lazy="dynamic", backref="organisation")
    #
    # # temporary only, as we need to store the reports somewhere for now
    # reports = relationship("Report", lazy="dynamic", backref="organisation")
    #
    constants = relationship("Constant", lazy="dynamic", backref="organisation")

    historians = relationship(Historian, lazy="dynamic", backref="organisation")
    #
    # settings = association_proxy('settings_association', 'settings', creator=lambda s: OrganisationSetting(setting=s))
