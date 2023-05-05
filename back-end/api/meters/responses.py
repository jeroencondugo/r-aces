#  Copyright (c) 2015-2020 Condugo bvba

from marshmallow import fields

from cdg_service.schemes import MeasureSchema, MeterConfigField, MeterTypeSchema, meter_schema, meter_read_schema, meter_changeset_schema
from cdg_service.schemes.api_response import ApiResponse


class MeterConfigResponseSchema(ApiResponse):
    params = fields.Dict(description='Input parameters', required=True, default={})
    response = MeterConfigField(description='', required=True)


class MeterConfigsResponseSchema(ApiResponse):
    params = fields.Dict(description='Input parameters', required=True, default={})
    response = fields.List(MeterConfigField, description='', required=True)


def meters_response_schema(model_cls: 'Meter'):
    class MetersResponseSchema(ApiResponse):
        params = fields.Dict(description='Input parameters', required=True, default={})
        response = fields.Nested(meter_read_schema(model_cls), description='', many = True, required=True)

    return MetersResponseSchema


def meter_response_schema(model_cls: 'Meter', ip_model_cls: 'GraphNodePortInput', op_model_cls: 'GraphNodePortOutput'):
    class MeterResponseSchema(ApiResponse):
        params = fields.Dict(description='Input parameters', required=True, default={})
        response = fields.Nested(meter_schema(model_cls, ip_model_cls, op_model_cls), description='', required=True)

    return MeterResponseSchema


def meter_changeset_response_schema(model_cls: 'Meter', ip_model_cls: 'GraphNodePortInput', op_model_cls: 'GraphNodePortOutput'):
    class MeterChangesetResponseSchema(ApiResponse):
        params = fields.Dict(description='Input parameters', required=True, default={})
        response = fields.Nested(meter_changeset_schema(model_cls, ip_model_cls, op_model_cls), description='', required=True)

    return MeterChangesetResponseSchema


class MeterTypesResponseSchema(ApiResponse):
    params = fields.Dict(description='Input parameters', required=True, default={})
    response = fields.Nested(MeterTypeSchema, description='', many = True, required=True)


class MeasuresResponseSchema(ApiResponse):
    params = fields.Dict(description='Input parameters', required=True, default={})
    response = fields.Nested(MeasureSchema, description='', many=True, required=True)


class MeterCategoriesResponseSchema(ApiResponse):
    params = fields.Dict(description='Input parameters', required=True, default={})
    response = fields.List(fields.String, description='', required=True)
