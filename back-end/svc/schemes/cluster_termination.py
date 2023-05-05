from aenum import IntEnum
from marshmallow import fields, Schema

from cdglib.models_general.security import ClusterMembershipTermination
from cdg_service.schemes.base_schema import base_schema
from cdg_service.schemes.api_response import ApiResponse


class TerminationExpired(IntEnum):
    YES = 1
    NO = 2


class ClusterTerminationBaseSchema(base_schema(ClusterMembershipTermination, exclude_fields=['accepted', 'expires_at', 'status'])):
    client_id = fields.Integer(required=True)
    cluster_id = fields.Integer(required=True)
    days_valid = fields.Integer(default=None, missing=None)


class CreateClusterTerminationSchema(ClusterTerminationBaseSchema):
    pass


class ClusterTerminationSchema(base_schema(ClusterMembershipTermination, exclude_fields=['client', 'cluster'])):
    client_id = fields.Integer(required=True)
    cluster_id = fields.Integer(required=True)
    accepted = fields.Boolean(required=True, dump_only=True, default=None, missing=None)
    expires_at = fields.DateTime(required=True, dump_only=True)
    status = fields.Function(lambda obj: obj.status)


class UpdateClusterTerminationSchema(base_schema(ClusterMembershipTermination, exclude_fields=['client_id', 'cluster_id', 'expires_at', 'status'])):
    accepted = fields.Boolean(required=True, default=False, missing=False)


class ClusterTerminationResponseSchema(ApiResponse):
    response = fields.Nested(ClusterTerminationSchema, description='', required=True)


class ClusterTerminationsResponseSchema(ApiResponse):
    response = fields.Nested(ClusterTerminationSchema, description='', many=True, required=True)
