# from cdglib.models_client import Organisation, Site
from datetime import datetime

from marshmallow import fields, Schema
from marshmallow_enum import EnumField

from cdg_service.schemes.api_response import ApiResponse
from cdg_service.schemes.base_schema import base_schema
from cdglib.models_general.security import Cluster, ClusterType


class BanSchema(Schema):
    subject = fields.Integer(required=True)
    issuer = fields.Integer(required=True)
    timestamp = fields.String(required=False, default=datetime.utcnow().isoformat())
    reason = fields.String(required=False, default="Not specified")


class UserRoleSchema(Schema):
    user_id = fields.Integer(required=True)
    role_id = fields.Integer(required=True)
    domain_id = fields.Integer(required=False)


class ClusterClientSchema(Schema):
    cluster_id = fields.Integer(required=True)
    client_id = fields.Integer(required=True)


class ClusterSchema(base_schema(Cluster, exclude_fields=['_type', 'schema_user', '_schema_password', 'membership_terminations', 'invites', 'users_default', 'users', 'cluster_clients'])):
    cluster_type = EnumField(ClusterType, default=ClusterType.STANDARD, missing=ClusterType.STANDARD, dump_only=True)
    user_roles = fields.Nested(UserRoleSchema, many=True, default=[], missing=[], dump_only=True)
    banned_clients = fields.List(fields.Integer, default=[], missing=[], dump_only=True)


class UpdateClusterSchema(base_schema(Cluster, exclude_fields=['schema', '_schema_password', 'users', 'user_roles', 'users_default', 'invites', 'membership_terminations'])):
    id = fields.Integer(required=True)
    schema_user = fields.String()
    schema_password = fields.String()
    cluster_type = EnumField(ClusterType, default=ClusterType.STANDARD, missing=ClusterType.STANDARD, by_value=True)
    user_roles = fields.Method("dump_user_roles", deserialize="load_user_roles")

    def dump_user_roles(self, obj):
        return []

    def load_user_roles(self, value):
        # if self.instance:
        #     role_users = defaultdict(list)
        #     for ur in value:
        #         role_users[ur["role_id"]].append(ur["user_id"])
        #
        #     for role, users in role_users.items():
        #         self.instance.add_users(role_id=role, users=users)
        #
        #     self.session.add(self.instance)

        return []


class CreateClusterSchema(UpdateClusterSchema):
    class Meta(UpdateClusterSchema.Meta):
        exclude = ['id', '_schema_password', 'users', 'users_default', 'invites', 'membership_terminations', 'deleted']

    name = fields.String(required=True)
    # user_roles = fields.Nested(UserRoleSchema, many=True, default=[], missing=[])



class ClusterResponseSchema(ApiResponse):
    response = fields.Nested(ClusterSchema, description='', required=True)


class ClustersDeletedResponseSchema(ApiResponse):
    response = fields.List(fields.Integer, description='', required=True)


class ClustersResponseSchema(ApiResponse):
    response = fields.Nested(ClusterSchema, description='', many=True, required=True)


class ClusterBansResponseSchema(ApiResponse):
    response = fields.Nested(BanSchema, description='', many=True, required=True)
