from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from cdglib.models_general.security import Domain, DomainType
from cdg_service.schemes.base_schema import base_schema
from cdg_service.schemes.api_response import ApiResponse
from cdg_service.schemes.relationship_schemes import UserRoleSchema


class FileSchema(Schema):
    filename = fields.String(required=True)
    interval = fields.String(required=False)
    regular_data = fields.Bool()
    synchronized_data = fields.Bool()
    repeat_data = fields.Bool()
    apply_delta = fields.Bool()


class FileSchema(base_schema(Domain, exclude_fields=['_type', '_schema', 'schema_user', '_schema_password'])):
    type = EnumField(DomainType)
    uid = fields.Function(lambda obj: obj.uid)
    schema = fields.Function(lambda obj: obj.schema)
    users = fields.Method('get_users', attribute='users')

    def get_users(self, obj):
        serializer = UserRoleSchema(many=True)
        return serializer.dump(obj.users).data


class FileResponseSchema(ApiResponse):
    response = fields.Nested(FileSchema, description='File analysis objects', required=True)


class FilesResponseSchema(ApiResponse):
    response = fields.String(many=True)


class FileTypeSchema(Schema):
    name = fields.String()
    extensions = fields.String(many=True)


class FileTypesResponseSchema(ApiResponse):
    response = fields.Nested(FileTypeSchema, many=True, description='File types')