#  Copyright (c) 2015-2021 Condugo bvba

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr

from cdglib.database import ClusterBase
from cdglib.models_domain import BasetreeBase


class Basetree(ClusterBase, BasetreeBase):
    __tablename__ = 'basetree'
    __table_args__ = {'schema' : 'clusterschema'}

    @declared_attr
    def organisation_id(self):
        return Column(Integer, ForeignKey('clusterschema.organisation.id'), index=True)

    def __init__(self, name="", order=0, locked=False, bt_type="standard", label='', add_level_locked=False):
        BasetreeBase.__init__(self, name=name, order=order, locked=locked, bt_type=bt_type, label=label, add_level_locked=add_level_locked)
