from marshmallow import fields
from marshmallow.exceptions import MarshmallowError
from marshmallow_sqlalchemy import ModelSchema

from cdg_service.schemes.api_response import ApiResponse

from cdg_service.schemes.base_schema import base_schema
from cdg_service.schemes.polymorphic_schema import PolymorphicSchema
from cdglib.models_client import FileImporter, FileImporterGlob, FileImporterOptions


class BaseFileImporterSchema(ModelSchema):
    class Meta:
        ordered = True
        model = FileImporter
        exclude = ["_type"]

    id = fields.Integer(dump_only=True, required=True)
    start_date = fields.DateTime(default=None, allow_none=True)
    end_date = fields.DateTime(default=None, allow_none=True) # Function(lambda obj: obj.start_date.isoformat() if obj.start_date else None, )
    globs = fields.Function(lambda obj: [glob.id for glob in obj.globs] if obj and obj.globs else [], dump_only=True)
    options = fields.Function(lambda obj: [opt.id for opt in obj.options] if obj and obj.options else [], dump_only=True)
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=False)

    def dump_type(self, obj):
        """ Convert type enum to class name """
        return obj.type

    def load_type(self, value):
        """ Load class name into enum _type field """
        return value


class FileImporterExcelSchema(BaseFileImporterSchema):
    pass

class FileImporterMaxeeSchema(BaseFileImporterSchema):
    base_url = fields.String(required=True)
    api_key = fields.String(required=True)
    company_name = fields.String(required=True)
    division = fields.String(required=True)


class FileImporterCsvSchema(BaseFileImporterSchema):
    delimiter = fields.String(required=True)
    decimal_separator = fields.String(required=True)


class FileImporterDsoSchema(BaseFileImporterSchema):
    pass


class FileImporterMbusSchema(BaseFileImporterSchema):

    pass


class FileImporterExcelCreateSchema(FileImporterExcelSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterMaxeeCreateSchama(FileImporterMaxeeSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterCsvCreateSchema(FileImporterCsvSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)


class FileImporterDsoCreateSchema(FileImporterDsoSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)


class FileImporterMbusCreateSchema(FileImporterMbusSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)


class FileImporterExcelUpdateSchema(FileImporterExcelSchema):
    id = fields.Integer(required=True)

class FileImporterMaxeeUpdateSchema(FileImporterMaxeeSchema):
    id = fields.Integer(required=True)

class FileImporterCsvUpdateSchema(FileImporterCsvSchema):
    id = fields.Integer(required=True)


class FileImporterDsoUpdateSchema(FileImporterDsoSchema):
    id = fields.Integer(required=True)


class FileImporterMbusUpdateSchema(FileImporterMbusSchema):
    id = fields.Integer(required=True)


class FileImporterSchema(PolymorphicSchema):
    type_field = "type"
    type_field_remove = False

    type_schemas = {
        'FileImporterCsv': FileImporterCsvSchema,
        'FileImporterExcel': FileImporterExcelSchema,
        'FileImporterDso': FileImporterDsoSchema,
        'FileImporterMbus': FileImporterMbusSchema,
        'FileImporterMaxee': FileImporterMaxeeSchema,
    }


class FileImporterCreateSchema(FileImporterSchema):
    type_schemas = {
        'FileImporterCsv': FileImporterCsvCreateSchema,
        'FileImporterExcel': FileImporterExcelCreateSchema,
        'FileImporterDso': FileImporterDsoCreateSchema,
        'FileImporterMbus': FileImporterMbusCreateSchema,
        'FielImporterMaxee': FileImporterMaxeeCreateSchama,
    }


class FileImporterUpdateSchema(FileImporterSchema):
    type_schemas = {
        'FileImporterCsv': FileImporterCsvUpdateSchema,
        'FileImporterExcel': FileImporterExcelUpdateSchema,
        'FileImporterDso': FileImporterDsoUpdateSchema,
        'FileImporterMbus': FileImporterMbusUpdateSchema,
        'FileImporterMaxee': FileImporterMaxeeUpdateSchema,
    }


class FileImportersResponseSchema(ApiResponse):
    response = fields.List(fields.Nested(FileImporterSchema, description='', required=True), default=[])


class FileImporterResponseSchema(ApiResponse):
    response = fields.Nested(FileImporterSchema, description='', required=True)

# *************************** File Importer Glob Schemas ****************************


class FileImporterGlobSchema(base_schema(FileImporterGlob, exclude_fields=["importer"])):
    importer_id = fields.Function(lambda obj: obj.importer_id)


class FileImporterGlobResponseSchema(ApiResponse):
    response = fields.Nested(FileImporterGlobSchema, description="", many=False, required=True)


class FileImporterGlobsResponseSchema(ApiResponse):
    response = fields.List(fields.Nested(FileImporterGlobSchema, description="", many=False, required=True), default=[])

# *************************** File Importer Options Schemas ****************************


class BaseFileImporterOptionsSchema(ModelSchema):
    class Meta:
        ordered = True
        model = FileImporterOptions
        exclude = ["_type", "crontab", "importer"]

    id = fields.Integer(dump_only=True, required=True)
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=False)
    start_date = fields.DateTime(default=None, allow_none=True)
    end_date = fields.DateTime(default=None, allow_none=True)
    meter_id = fields.Integer()
    importer_id = fields.Integer()


    def dump_type(self, obj):
        """ Convert type enum to class name """
        return obj.type

    def load_type(self, value):
        """ Load class name into enum _type field """
        return value


class FileImporterCommonCsvExcelOptionsSchema(BaseFileImporterOptionsSchema):
    timestamp_column_id = fields.Integer()
    separate_time_column_id = fields.Integer(allow_none=True)
    timestamp_format = fields.String()
    separate_time_format = fields.String(allow_none=True)
    column_id = fields.Integer(allow_none=True)
    column_name = fields.String(allow_none=True)
    column_name_at_row = fields.Integer(allow_none=True)
    value_start_at_row = fields.Integer()


class FileImporterCsvOptionsSchema(FileImporterCommonCsvExcelOptionsSchema):
    name_column_id = fields.Integer()
    name = fields.String()
    csv_type = fields.String(required=True, default="Table")
    pass


class FileImporterExcelOptionsSchema(FileImporterCommonCsvExcelOptionsSchema):
    sheet_name = fields.String()
    transpose = fields.Boolean()

class FileImporterMaxeeOptionsSchema(BaseFileImporterOptionsSchema):
    device = fields.String(required=True)
    channel = fields.String(required=True)


class FileImporterDsoOptionsSchema(BaseFileImporterOptionsSchema):
    infrax_ean = fields.String(required=True)
    infrax_measure = fields.String(required=True)
    infrax_unit = fields.String(required=True)
    pass


class FileImporterMbusOptionsSchema(BaseFileImporterOptionsSchema):
    mbus_column = fields.Integer()
    mbus_id = fields.String()

class FileImporterExcelOptionsCreateSchema(FileImporterExcelOptionsSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterCsvOptionsCreateSchema(FileImporterCsvOptionsSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterMbusOptionsCreateSchema(FileImporterMbusOptionsSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterMaxeeOptionsCreateSchema(FileImporterMaxeeOptionsSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterDsoOptionsCreateSchema(FileImporterDsoOptionsSchema):
    type = fields.Method(serialize="dump_type", deserialize="load_type", required=True)

class FileImporterCsvOptionsUpdateSchema(FileImporterCsvOptionsSchema):
    id = fields.Integer(required=True)

class FileImporterMaxeeOptionsUpdateSchema(FileImporterMaxeeOptionsSchema):
    id = fields.Integer(required=True)

class FileImporterExcelOptionsUpdateSchema(FileImporterExcelOptionsSchema):
    id = fields.Integer(required=True)


class FileImporterDsoOptionsUpdateSchema(FileImporterDsoOptionsSchema):
    id = fields.Integer(required=True)


class FileImporterMbusOptionsUpdateSchema(FileImporterMbusOptionsSchema):
    id = fields.Integer(required=True)


class FileImporterOptionsSchema(PolymorphicSchema):
    type_field = "type"
    type_field_remove = False

    type_schemas = {
        'FileImporterCsvOptions': FileImporterCsvOptionsSchema,
        'FileImporterExcelOptions': FileImporterExcelOptionsSchema,
        'FileImporterDsoOptions': FileImporterDsoOptionsSchema,
        'FileImporterMbusOptions': FileImporterMbusOptionsSchema,
        'FileImporterMaxeeOptions': FileImporterMaxeeOptionsSchema
    }


class FileImporterOptionsCreateSchema(FileImporterOptionsSchema):
    type_schemas = {
        'FileImporterCsvOptions': FileImporterCsvOptionsCreateSchema,
        'FileImporterExcelOptions': FileImporterExcelOptionsCreateSchema,
        'FileImporterDsoOptions': FileImporterDsoOptionsCreateSchema,
        'FileImporterMbusOptions': FileImporterMbusOptionsCreateSchema,
        'FileImporterMaxeeOptions': FileImporterMaxeeOptionsCreateSchema,
    }


class FileImporterOptionsUpdateSchema(FileImporterOptionsSchema):
    type_schemas = {
        'FileImporterCsvOptions': FileImporterCsvOptionsUpdateSchema,
        'FileImporterExcelOptions': FileImporterExcelOptionsUpdateSchema,
        'FileImporterDsoOptions': FileImporterDsoOptionsUpdateSchema,
        'FileImporterMbusOptions': FileImporterMbusOptionsUpdateSchema,
        'FileImporterMaxeeOptions': FileImporterMaxeeOptionsUpdateSchema,
    }


class FileImporterOptionResponseSchema(ApiResponse):
    response = fields.Nested(FileImporterOptionsSchema)


class FileImporterOptionsResponseSchema(ApiResponse):
    response = fields.List(fields.Nested(FileImporterOptionsSchema), default=[])
