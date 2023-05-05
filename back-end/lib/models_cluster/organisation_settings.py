#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, ForeignKey, Integer
# from sqlalchemy.orm import relationship, backref

from cdglib.database import ClusterBase
# from cdglib.models_general.user_settings import UserSetting
from cdglib.models_domain.organisation_settings import OrganisationSettingBase


class OrganisationSetting(ClusterBase, OrganisationSettingBase):
    __tablename__ = 'ass_organisation_settings'
    __table_args__ = {'schema': 'clusterschema'}

    organisation_id = Column(Integer, ForeignKey('clusterschema.organisation.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    # organisation = relationship('Organisation', backref=backref('settings_association', cascade='save-update, merge, delete, delete-orphan'))

    # setting_id = Column(Integer, ForeignKey('general.settings.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    # setting = relationship('Setting', backref=backref('organisations_association', cascade='save-update, merge, delete, delete-orphan'))
