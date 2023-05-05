#  Copyright (c) 2015-2020 Condugo bvba
import datetime
import time
import os
import dateutil
import flask
from flask import request, current_app, g, send_from_directory
from pydantic import ValidationError

from cdg_service import ServiceCatalog
from cdg_service.service_context import service_context
from cdglib import scoped_client_session, MeasureRegister
from api.v2.blueprint import blueprint
from cdg_service.service.meter import MeterService, MeterNodeChangesResponse, MeterNodeChangesPayload
from cdglib.models_general.security import BuiltinPermission
from api.access_decorators import permissions_requires_one
from api.classmap import classmap_client, classmap_cluster
from api.v2.api_response import make_response
from cdglib.period import Period
from cdglib.resolution import Resolution
from .responses import MeterTypesResponseSchema, MeasuresResponseSchema
from cdg_service.profiles import ProfileCatalog

#from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename

# service = MeterService()
# pagination_schema = PaginationSchema()
from ...jwt_handlers import token_required

timing_profile = ProfileCatalog.get(ProfileCatalog.PROFILING)


@blueprint.route('/<client>/meters/<int:id>', methods=['GET'])
@permissions_requires_one(BuiltinPermission.METERS_READ)
def read_single_meter(client, id):
    try:
        t0 = time.perf_counter()
        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MetersResponseSchema()
        with service_context(ServiceCatalog.METER, client_id=client, echo=True, call_back=current_app.register_session) as service:
            meters = service.read(meter_ids=id)
            resp = make_response(schema, meters, 'Meters listed')
            t1 = time.perf_counter()
            print(f"Used {t1 - t0} seconds")
        return resp
    except Exception as e:
        return make_response(schema, None, str(e), status_code=e.code)


@blueprint.route('/<client>/meters', methods=['GET'])
@permissions_requires_one(BuiltinPermission.METERS_READ)
def read_meter(client):
    try:
        t0 = time.perf_counter()
        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MetersResponseSchema()
        with service_context(ServiceCatalog.METER, client_id=client, call_back=current_app.register_session) as service:
            meters = service.read(nodes=True)
            resp = make_response(schema, meters, 'Meters listed')
            t1 = time.perf_counter()
            print(f"Used {t1 - t0} seconds")
        return resp
    except Exception as e:
        return make_response(schema, None, e.message, status_code=e.code)


@blueprint.route('/<client>/meters/<int:id>/test', methods=['GET'])
@permissions_requires_one(BuiltinPermission.METERS_READ)
def test_single_meter(client, id):
    try:
        t0 = time.perf_counter()
        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MeterResponseSchema()
        with service_context(ServiceCatalog.METER, client_id=client, echo=True, call_back=current_app.register_session) as service:
            meter = service.test(id=id)
            if meter:
                resp = make_response(schema, meter, f'Meter {id} tested')
                t1 = time.perf_counter()
                print(f"Used {t1 - t0} seconds")
            else:
                resp = make_response(None, {}, f'Failed to test meter {id}!', status_code=400)
                t1 = time.perf_counter()
                print(f"Used {t1 - t0} seconds")
        return resp
    except Exception as e:
        return make_response(schema, None, str(e), status_code=e.code)


@blueprint.route('/<client>/meters', methods=['POST'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_CREATE)
def create_meter(client):
    try:
        kwargs = request.get_json()
        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MeterResponseSchema()

        with service_context(ServiceCatalog.METER, client_id=client, call_back=current_app.register_session) as service:
            # param = ReadParam(Meter, page, items_per_page)
            meter = service.create(**kwargs)
            service.session.commit()
            response = make_response(schema, meter, 'Meter created')
        return response
    except Exception as e:
        return make_response(schema, None, 'Failed to create meter', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/meters/<int:id>', methods=['PATCH'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def update_meter(client, id):
    try:
        # meter_id = request.args.get('meter_id')
        config_id = request.args.get('config_id')

        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MeterResponseSchema()
        json_data = request.get_json()
        with service_context(ServiceCatalog.METER, client_id=client, call_back=current_app.register_session) as service:
            # param = ReadParam(Meter, page, items_per_page)
            meter = service.update(id, config_id, json_data)
            service.session.commit()
            return make_response(schema, meter, 'Meter configuration updated')
    except Exception as e:
        return make_response(schema, None, 'Failed to update meter configuration', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/meters/<int:id>', methods=['DELETE'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_DELETE)
def delete_meter(client, id):
    # """
    # Delete meter with id.
    # ---
    # tags: ['Meter Management']
    # description: Delete user meter id.
    # parameters:
    #   - name: client
    #     in: path
    #     type: string
    #     required: true
    #     description: Name of the client
    #   - name: id
    #     in: path
    #     type: integer
    #     required: true
    #     description: ID of the meter
    # responses:
    #   200:
    #     description: Meter has been deleted.
    #     schema:
    #       $ref: '#/definitions/MeterResponse'
    #   404:
    #     description: Client or Meter not found.
    # """
    try:
        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MeterResponseSchema()
        # meters = []

        with scoped_client_session(client, call_back=current_app.register_session) as session:
            # param = ReadParam(Meter, page, items_per_page)
            service = MeterService(session)
            meter = service.delete(id)

            return make_response(schema, meter, 'Meter deleted')
    except Exception as e:
        return make_response(schema, None, 'Failed to delete meter', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/meters/set_source_config', methods=['PATCH'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def set_source_config(client):
    try:
        meter_id = request.args.get('meter_id', type=int)
        config_id = request.args.get('config_id', type=int)

        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MeterResponseSchema()
        # meters = []

        with scoped_client_session(client, call_back=current_app.register_session) as session:
            # param = ReadParam(Meter, page, items_per_page)
            service = MeterService(session)
            meter = service.set_source_config(meter_id, config_id)

            return make_response(schema, meter, 'Meter source configuration set')
    except Exception as e:
        return make_response(schema, None, 'Failed to set meter source configuration', error_msg=str(e), status_code=404)


@blueprint.route('/<domain>/meters/heatmap/config', methods=['GET'])
@permissions_requires_one(BuiltinPermission.HEATMAP_READ)
def get_heatmap_config(domain):
    """ Fetch the config for the heatmap based on the provided measure
        arg: measure: int, the measure_id
        {
            "begin": str, isoformat datetime
            "end": str, isoformat datetime
            "resolutions": {
                'W': ['QH', 'H'],
                'M': ['H'],
            }
        }

    """
    measure_id = flask.request.args.get("measure", type=int, default=None)
    measure = MeasureRegister.get_id(measure_id)
    output = {
        "start_date": datetime.datetime(2019, 1, 1, 0, 0, 0).isoformat(),
        "end_date": datetime.datetime.now().isoformat(),
        "resolutions": {
            'D': [],
            'W': ['QH', 'H'],
            'M': ['H'],
            'Q': [],
            'Y': [],
            'All': []
        }
    }
    resp = make_response(None, output, message=f"Heatmap config provided!")
    return resp


@blueprint.route('/<domain>/meters/heatmap', methods=['GET'])
@permissions_requires_one(BuiltinPermission.HEATMAP_READ)
def get_heatmap_meter_data(domain):
    """ Fetch the heatmap meter data
        {
            "excess": List[int],
            "demand": List[int],
            "period": Period,
            "resolution": Resolution,
            "start_date": datetime_isoformat,
            "measure": int
        }
        response: [
            {
                "id": Literal[0,1,2],
                "order": Literal[0,1,2],
                "type": Literal["excess", "demand"],
                "title": str,
                "measure": int,
                "data": List[Tuple[str, str, float]]
            }
        ]
    """
    default_resolution = Resolution.QUARTER_HOUR
    try:
        excess = flask.request.args.get("excess", type=str, default="")
        excess = [int(x) for x in excess.split(',')] if excess else []
        demand = flask.request.args.get("demand", type=str, default="")
        demand = [int(x) for x in demand.split(',')] if demand else []
        period = Period.from_string(flask.request.args.get("period", type=str, default=None))
        resolution = Resolution.from_string(flask.request.args.get("resolution", type=str, default=default_resolution))
        start_date_arg = flask.request.args.get("startDate", type=str, default=None)
        if not start_date_arg:
            return make_response(None, None, 'Failed to get heatmap data, startDate is missing or has errors!', error_msg='Failed to get heatmap data, startDate is missing or has errors!',
                                 status_code=404)
        start_date = datetime.datetime.fromisoformat(start_date_arg)
        measure_id = flask.request.args.get("measure", type=int, default=None)
        if not measure_id:
            return make_response(None, None, 'Failed to get heatmap data, measure is missing or has errors!', error_msg='Failed to get heatmap data, measure is missing or has errors!',
                                 status_code=404)
        measure = MeasureRegister.get_id(measure_id)
        with service_context(ServiceCatalog.METER, client_id=domain, call_back=current_app.register_session) as service:
            dfs_meta = [
                {"type": "excess", "title": "Sum of the excess meters"},
                {"type": "demand", "title": "Sum of the demand meters"},
                {"type": "overlap", "title": "Energy overlap between excess and demand"},
                {"type": "difference", "title": "Energy difference between excess and demand"},
            ]
            dfs = service.get_heatmap_meter_data(excess, demand, period, resolution, start_date, measure)
            output = []
            for index, df_tuple in enumerate(zip(dfs, dfs_meta)):
                df = df_tuple[0]
                if df is None: continue
                data_rows = []
                for dt_index, row in df.iterrows():
                    dt_index = dt_index.tz_localize(None)
                    row_tuple = (dt_index.date().isoformat(), dt_index.isoformat(), row['val'])
                    data_rows.append(row_tuple)
                df_dict = {
                    "id": index,
                    "order": index,
                    "type": df_tuple[1]["type"],
                    "title": df_tuple[1]["title"],
                    "data": data_rows
                }
                output.append(df_dict)
            resp = make_response(None, output, message=f"Heatmap data provided!")
        return resp
    except Exception as e:
        return make_response(None, None, 'Failed to get heatmap data!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/meters/<id>/values', methods=['GET'])
@permissions_requires_one(BuiltinPermission.METERS_READ)
def get_meter_data(client, id):
    """

    :param
        - client: client_id
        - id meter_id
    :return:
    """
    default_resolution = Resolution.QUARTER_HOUR
    try:
        period = Period.from_string(flask.request.args.get("period", type=str, default=None))
        resolution = Resolution.from_string(
            flask.request.args.get("resolution", type=str, default=default_resolution))
        start_date = flask.request.args.get("start_date", type=str, default=None)
        start_date = datetime.datetime.combine(dateutil.parser.parse(start_date),
                                               datetime.time.min) if start_date else start_date
        with service_context(ServiceCatalog.METER, client_id=client, call_back=current_app.register_session) as service:
            data = service.get_meter_data([id], period, resolution, start_date)
            resp = make_response(None, data, message=f"Data with id{id} given")
        return resp
    except Exception as e:
        return make_response(None, None, 'Failed to get meter data!', error_msg=str(e), status_code=404)


# @blueprint.route('/<string:client>/meter/<int:id>/values/', methods=['GET'], profile=timing_profile)
# @permissions_requires_one(BuiltinPermission.METERS_READ)
# def meter_values(client, id):
#     # """
#     # List meter values.
#     # ---
#     # tags: ['Meter Management (v2)']
#     # description: List meter values.
#     # parameters:
#     #   - name: client
#     #     in: path
#     #     type: string
#     #     required: true
#     #     description: Name of the client
#     #   - name: id
#     #     in: path
#     #     type: integer
#     #     required: true
#     #     description: ID of the meter
#     # responses:
#     #   200:
#     #     description: Meter(s) listed.
#     #     schema:
#     #       $ref: '#/definitions/MetersResponse'
#     #   400:
#     #     description: Meter(s) not found.
#     # """
#     try:
#         page = request.args.get('page')
#         items_per_page = request.args.get('items_per_page')

#         kwargs = {}
#         if page and items_per_page:
#             kwargs['pagination'] = {'page': page, 'items_per_page': items_per_page}

#         schema = MetersResponseSchema()
#         # meters = []

#         with scoped_client_session(client) as session:
#             param = ReadParam(Meter, page, items_per_page)
#             service = MeterService(session)
#             meters = service.read(param)

#             return make_response(schema, meters, 'Meters read', **kwargs)

#     except Exception as e:
#         return make_response(schema, None, 'Failed to read meters', error_msg=str(e), status_code=404)


@blueprint.route('/gen/meter_types', methods=['GET'])
@permissions_requires_one(BuiltinPermission.METERS_READ)
def get_meter_types():
    """
    List all meter types.
    ---
    tags: ['Meter Management']
    description: List all meter types.
    responses:
      200:
        description: Meter type(s) listed.
        schema:
          $ref: '#/definitions/MeterTypesResponse'
      400:
        description: Meter type(s) not found.
    """
    schema = MeterTypesResponseSchema()
    service = MeterService()

    meter_types = service.types()

    return make_response(schema, meter_types, 'Meter types listed!')


@blueprint.route('/<string:client>/meters/<int:id>/apply_changeset', methods=['PATCH'], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def apply_changeset(client, id):
    try:
        # page = request.args.get('page')
        # items_per_page = request.args.get('items_per_page')

        # kwargs = {}
        # if page and items_per_page:
        #     kwargs['pagination'] = {'page': page, 'items_per_page': items_per_page}

        classmap = classmap_cluster if client.startswith("cl_") else classmap_client
        schema = classmap.MeterChangesetResponseSchema()
        changeset = request.get_json()

        # meters = []

        with service_context(ServiceCatalog.METER, client_id=client, call_back=current_app.register_session) as service:
            # param = ReadParam(Meter, page, items_per_page)
            meter = service.apply_changeset(id, changeset)

            return make_response(schema, meter, 'Meters changeset applied')

    except Exception as e:
        return make_response(None, None, 'Failed to apply changeset on meters', error_msg=str(e), status_code=500)


@blueprint.route('/gen/measures', methods=["GET"])
@token_required()
def get_measures():
    """
    List all measurements.
    ---
    tags: ['Meter Management']
    description: List all measurements.
    responses:
      200:
        description: Measurement(s) listed.
        schema:
          $ref: '#/definitions/MeasuresResponse'
      400:
        description: Measurement(s) not found.
    """
    try:
        schema = MeasuresResponseSchema()
        service = MeterService()

        measures = service.measures()

        return make_response(schema, measures, 'Measures listed!')
    except Exception as e:
        return make_response(schema, None, 'Failed to list measures', status_code=500)


# @blueprint.route('/<client>/meters/values',methods=["POST"], profile=timing_profile)
# @permissions_requires_one(BuiltinPermission.METERS_CREATE)
# def post_values(client):
#     try:
#         with service_context(ServiceCatalog.METER, session=g.session) as service:
#             values = service.create_values(request.get_json(silent=True)['meters'])

#             return make_response(None, values, 'Meter values created!')
#     except:
#         return make_response(None, None, 'Failed to create meter values!', status_code=500)


# @blueprint.route('/<client>/meters/<int:id>/values/', methods=["GET"], profile=timing_profile)
# @permissions_requires_one(BuiltinPermission.METERS_READ)
# def get_meter_values(client, id):
#     try:
#         with service_context(ServiceCatalog.METER, session=g.session) as service:
#             values = service.read_values(id)

#             return make_response(None, values, 'Meter values listed')
#     except Exception as e:
#         # TODO: use ApiError class
#         return make_response(None, None, 'Failed to read meter values', error_msg=str(e), status_code=500)


# @blueprint.route('/<client>/meters/<int:id>/values/',methods=["POST"], profile=timing_profile)
# @permissions_requires_one(BuiltinPermission.METERS_CREATE)
# def post_meter_values(client, id):
#     try:
#         with service_context(ServiceCatalog.METER, session=g.session) as service:
#             values = service.create_meter_values(id, request.get_json(silent=True))

#             return make_response(None, values, 'Meter values created!')
#     except:
#         return make_response(None, None, 'Failed to create meter values!', status_code=500)


# @blueprint.route('/<client>/meters/<int:id>/values',methods=["PATCH"], profile=timing_profile)
# @permissions_requires_one(BuiltinPermission.METERS_UPDATE)
# def patch_meter_values(client, id):
#     try:
#         with service_context(ServiceCatalog.METER, session=g.session) as service:
#             values = service.patch_meter_values(id, request.get_json(silent=True))

#             return make_response(None, values, 'Meter values updated!')
#     except:
#         return make_response(None, None, 'Failed to update meter values!', status_code=500)


@blueprint.route('/<client>/meters/attached_nodes', methods=["GET"])
@permissions_requires_one(BuiltinPermission.METERS_READ)
def meters_attached_nodes(client):
    try:
        with service_context(ServiceCatalog.METER, client_id=client, call_back=current_app.register_session) as service:
            # with service_context(ServiceCatalog.METER, session=g.session) as service:
            nodes = service.attached_nodes()

            return make_response(None, nodes, 'Meters with nodes listed!')
    except:
        return make_response(None, None, 'Failed to read meter attached nodes!', status_code=500)


@blueprint.route('/<client>/meters/node_changes', methods=["POST"], profile=timing_profile)
@permissions_requires_one(BuiltinPermission.METERS_UPDATE)
def meters_node_changes(client):
    payload = request.get_json(silent=True)
    try:
        changes = MeterNodeChangesPayload(**payload)
        print(changes)
    except ValidationError as e:
        return make_response(None, MeterNodeChangesResponse(), error_msg=str(e))
    with service_context(ServiceCatalog.METER, client_id=client, session=g.session, call_back=current_app.register_session) as service:
        successful_changes, failed_changes = service.apply_node_changes(changes)
        return make_response(None, MeterNodeChangesResponse(successful_changes, failed_changes), 'Meter connection changes processed')

# @blueprint.route('/<string:client>/meters/import_from_file', methods=['POST'], profile=timing_profile)
# @permissions_requires_one(BuiltinPermission.METERS_CREATE)
# def import_from_file(client):
#     #try:
#     with scoped_client_session(client) as session:
#         meter_type = MeterType.MANUAL
#         measure_id = 2000
#         meter_service = MeterService(session)
#         file_service = FileService(session)
#         unreferenced_csv_files = file_service.read(["csv"])
#         created_meters = meter_service.create_csv_meters(unreferenced_csv_files, repeat_data=False, meter_type=meter_type, measure_id=measure_id)
#     return make_response(None, None, 'Meters based on files created successfully')

#     #except:
#     #    return make_response(None, None, 'Failed to import meters from file!', status_code=500)



ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])
UPLOAD_FOLDER = '/opt/condugo/upload_folder'
EXAMPLE_EXCEL_FILENAME = './example_meter_upload.xlsx'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('/<client>/meters/import', methods=["POST"])
#@permissions_requires_one(BuiltinPermission.METERS_CREATE)
def meters_upload_file(client):
    # check if the post request has the file part

    def process_formfield(request, field_name: str):
        """ Get field value from ImmutableMultiDict """
        try:
            values = request.form.getlist(field_name)
            if len(values) > 0:
                return values[0]
            return None
        except Exception as e:
            print(e)

    skip_existing_meters = process_formfield(request, "skipExistingMeters")
    skip_meter_data = process_formfield(request, "skipMeterData")
    if 'file' not in request.files:
        return make_response(None, None, message='', error_msg='No file part in the request!', status_code=400)
    file = request.files['file']
    if file.filename == '':
        return make_response(None, None, message='', error_msg='No file selected for uploading!', status_code=400)
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        except Exception as e:
            print(e)
        return make_response(None, None, message='File successfully uploaded!', status_code=201)
    else:
        return make_response(None, None, message='', error_msg=f'Allowed file types: {ALLOWED_EXTENSIONS}', status_code=400)

@blueprint.route('/gen/meters/download_example', methods=['GET'])
#@permissions_requires_one(BuiltinPermission.METERS_READ)
def meters_download_example():
    # Returning file from appended path
    return send_from_directory(directory=UPLOAD_FOLDER, path=EXAMPLE_EXCEL_FILENAME, as_attachment=True)
