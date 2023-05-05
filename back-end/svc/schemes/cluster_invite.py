from typing import Union

from aenum import IntEnum
from marshmallow import fields, Schema, post_load, pre_load
from marshmallow_enum import EnumField

from cdglib.models_general.security import ClusterInvite
from cdg_service.schemes.base_schema import base_schema
from cdg_service.schemes.api_response import ApiResponse


class InviteExpired(IntEnum):
    YES = 1
    NO = 2
    BOTH = 3


# class Options(object):
#
#     def __init__(self, cluster_id: int = None, expired: InviteExpired = InviteExpired.BOTH):
#         self._cluster_id = cluster_id
#         self._expired = expired
#
#     @property
#     def cluster_id(self) -> Union[int, None]:
#         return self._cluster_id
#
#     @property
#     def expired(self) -> InviteExpired:
#         return self._expired
#
#     def filter(self) -> tuple:
#         options = []
#
#         if self.cluster_id:
#             options.append(ClusterInvite.cluster_id==self.cluster_id)
#
#         # if self.expired == InviteExpired.NO:
#
#
#         return tuple(options)
#
# class OptionsSchema(Schema):
#     cluster_id = fields.Integer(allow_none=True, default=None, missing=None)
#     expired = EnumField(InviteExpired, default=InviteExpired.BOTH, missing=InviteExpired.BOTH)
#
#     @pre_load
#     def set_options(self, data, **kwargs):
#         if "cluster_id" not in data:
#             data["cluster_id"] = None
#
#         if "expired" not in data:
#             data["expired"] = InviteExpired.BOTH.name
#
#         return data
#
#     @post_load
#     def make_filter(self, data, **kwargs):
#         return Options(**data)


class ClusterMembershipBaseSchema(base_schema(ClusterInvite, exclude_fields=['accepted', 'expires_at', 'status', 'client', 'cluster'])):
    client_id = fields.Integer(required=True)
    cluster_id = fields.Integer(required=True)
    days_valid = fields.Integer(default=None, missing=None)


class CreateClusterInviteSchema(ClusterMembershipBaseSchema):
    pass


class ClusterInviteSchema(base_schema(ClusterInvite, exclude_fields=['client', 'cluster'])):
    client_id = fields.Integer(required=True)
    cluster_id = fields.Integer(required=True)
    accepted = fields.Boolean(required=True, dump_only=True, default=None, missing=None)
    expires_at = fields.DateTime(required=True, dump_only=True)
    status = fields.Function(lambda obj: obj.status)
    received = fields.Boolean()


class UpdateClusterInviteSchema(base_schema(ClusterInvite, exclude_fields=['client', 'cluster', 'expires_at', 'status'])):
    accepted = fields.Boolean(required=True, default=False, missing=False)


class ClusterInviteResponseSchema(ApiResponse):
    response = fields.Nested(ClusterInviteSchema, description='', required=True)


class ClusterInvitesResponseSchema(ApiResponse):
    response = fields.Nested(ClusterInviteSchema, description='', many=True, required=True)
