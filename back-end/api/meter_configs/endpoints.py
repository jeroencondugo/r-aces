#  Copyright (c) 2015-2020 Condugo bvba

from flask import request, g, jsonify, current_app

from cdg_service import ServiceCatalog
from cdg_service.service_context import service_context
from cdglib import scoped_client_session
from cdglib.models_client.meter_configs import MeterConfig

# from api.schemes.meter_config import MeterConfigType
from cdglib.models_general.security import BuiltinPermission
from api.access_decorators import permissions_requires_one
from api.v2.blueprint import blueprint
from cdg_service.errors import ApiError
from cdg_service.service.meter_config import MeterConfigService
from cdg_service.schemes import MeterConfigType, MeterConfigResponseSchema, MeterConfigsResponseSchema, MeterConfigTypesResponseSchema#, PaginationSchema
# from api.services.cdg_service.schemes import serialize as serialize_configs #TODO: move serialize to proper place

from api.v2.api_response import make_response

from cdg_service.profiles import ProfileCatalog
timing_profile = ProfileCatalog.get(ProfileCatalog.PROFILING)

service = MeterConfigService()
# pagination_schema = PaginationSchema()


@blueprint.route('/<string:client>/meter/<int:id>/meterconfigs', methods=['GET'], profile=timing_profile)
#@permissions_requires_one(BuiltinPermission.METERS_READ)
def meter_configs(client, id):
    """
    List meter configs for a meter.
    ---
    tags: ['MeterConfig Management']
    description: List meter configs.
    parameters:
      - name: client
        in: path
        type: string
        required: true
        description: Name of the client
      - name: id
        in: path
        type: integer
        required: true
        description: ID of the meter
    responses:
      200:
        description: Meter config(s) listed.
        schema:
          $ref: '#/definitions/MeterConfigsResponse'
      400:
        description: Meter config(s) not found.
    """
    try:
        schema = MeterConfigsResponseSchema()

        with scoped_client_session(client, call_back=current_app.register_session) as session:
            service.session = session

            meter_configs = service.read(meter_ids=[id])
            # TODO: schema set to None due polymorphic field missing in base marshmallow library. change later
            resp = make_response(schema, meter_configs, 'Meter config(s) read')

    except ApiError as e:
        resp = make_response(schema, None, 'Failed to read meter config(s)', error_msg=e.message, status_code=e.code)

    return resp


@blueprint.route('/<string:client>/meter/<int:id>/meterconfigs', methods=['POST'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_CREATE)
def create_meter_config(client, id):
    try:
        schema = MeterConfigResponseSchema()

        with service_context(ServiceCatalog.METER_CONFIG, client_id=client, call_back=current_app.register_session) as _service:
            # config_type = request.args.get('type').lower()
            data = request.get_json()
            # TODO: copy paste from admin_app/cdg_admin/context/meter_config/create_meter_config_command.py
            # attr_dict['measure_id'] = data['measure']
            # if config_type == MeterConfigType.MeterConfigSQLA:
            #     attr_dict['driver'] = data['driver']
            #     attr_dict['database'] = data['database']
            #     attr_dict['server'] = data['server']
            #     attr_dict['uid'] = data['uid']
            #     attr_dict['pwd'] = data['pwd']
            #     attr_dict['port'] = data['port'] # TODO JvdM: Add validation for int
            #     attr_dict['table'] = data['table']
            #     attr_dict['tscol'] = data['tscol']
            #     attr_dict['valcol'] = data['valcol']
            # if config_type == MeterConfigType.MeterConfigSQLA:
            #     attr_dict['repeat_data'] = data['repeat_data'].lower() == 'true'
            #     attr_dict['apply_delta'] = data['apply_delta'].lower() == 'true'
            #     attr_dict['regular_data'] = data['regular_data'].lower() == 'true'
            #     attr_dict['synchronized_data'] = data['synchronized_data'].lower() == 'true'
            # if config_type == MeterConfigType.MeterConfigAdd or \
            #    config_type == MeterConfigType.MeterConfigBinaryOperator or \
            #    config_type == MeterConfigType.MeterConfigSQLA or \
            #    config_type == MeterConfigType.MeterConfigThermalPower:
            #     attr_dict['interval'] = data['interval']
            # if config_type == MeterConfigType.MeterConfigBinaryOperator:
            #     attr_dict['operator'] = data['operator']
            # if config_type == MeterConfigType.MeterConfigThermalPower:
            #     attr_dict['heat_capacity'] = data['heat_capacity'] # TODO JvdM: Add validation for float
            #     attr_dict['heating'] = data['heating'].lower() == 'true'
            # if config_type == MeterConfigType.MeterConfigMaxee:
            #     attr_dict['measurement_db_id'] = int(data['measurement_db_id'])
            #     attr_dict['device_id'] = int(data['device_id'])
            #     attr_dict['channel_id'] = int(data['channel_id'])

            configs = _service.create(id, **data)
            resp = make_response(schema, configs, 'Meter config created')

    except ApiError as e:
        resp = make_response(schema, None, 'Failed to create meter config', error_msg=e.message, status_code=e.code)

    return resp


@blueprint.route('/<string:client>/meter/<int:id>/meterconfigs', methods=['PATCH'])
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def update_meter_config(client, id):
    pass


@blueprint.route('/<string:client>/meterconfigs/<int:id>', methods=['DELETE'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def delete_meter_config(client, id):
    try:
        schema = MeterConfigResponseSchema()

        with scoped_client_session(client, call_back=current_app.register_session) as session:
            service.session = session

            config = service.delete(id)
            resp = make_response(schema, config, 'Meter config deleted')
    except ApiError as e:
        resp = make_response(schema, None, 'Failed to delete meter config', error_msg=e.message, status_code=e.code)

    return resp


@blueprint.route('/<string:client>/meterconfigs/<int:id>/connect_port', methods=['PATCH'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def connect_port(client, id):
    try:
        schema = MeterConfigResponseSchema()

        with scoped_client_session(client, call_back=current_app.register_session) as session:
            service.session = session

            config = service.connect_port(id, request.args.get('port_name'), int(request.args.get('source')))
            resp = make_response(schema, config, 'Meter port connected')
    except ApiError as e:
        resp = make_response(schema, None, 'Failed to connect meter port', error_msg=e.message, status_code=e.code)

    return resp


@blueprint.route('/<string:client>/meterconfigs/types', methods=['GET'], profile=timing_profile)
#@permissions_requires_one(BuiltinPermission.METERS_READ)
def meter_config_types(client):
    """
    Catalog of MeterConfig types.
    ---
    tags: ['MeterConfig']
    description: Catalog of MeterConfig types.
    consumes:
      - application/json
    parameters:
      - name: client
        in: path
        type: string
        required: true
        description: Name of the client
    responses:
      200:
        description: MeterConfig catalog items listed.
        schema:
          $ref: '#/definitions/MeterConfigTypesResponse'
      500:
        description: Internal server error.
        schema:
          $ref: '#/definitions/ApiErrorResponse'
    """
    try:
        schema = MeterConfigTypesResponseSchema()

        with scoped_client_session(client, call_back=current_app.register_session) as session:
            service.session = session

            catalog = 'cluster' if client.startswith("cl_") else 'client'
            types = service.types(catalog=catalog)
            resp = make_response(schema, types, 'MeterConfig types read')
    except ApiError as e:
        resp = make_response(schema, None, 'Failed to read MeterConfig types', error_msg=e.message, status_code=e.code)

    return resp
