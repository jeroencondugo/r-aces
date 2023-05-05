from flask import current_app

from api.access_decorators import permissions_requires_one, permissions_requires_all
from api.v2 import blueprint, request
from api.v2.api_response import make_response
from cdg_service import ServiceCatalog
from cdg_service.errors import ApiError
from cdg_service.schemes.file_imports import FileImporterResponseSchema, FileImportersResponseSchema
from cdg_service.service_context import service_context
from cdglib.models_general import BuiltinPermission


@blueprint.route("/<client>/file_imports", methods=["POST"])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_CREATE)
def create_file_importer(client):
    try:
        data = request.get_json()
        schema = FileImporterResponseSchema()

        with service_context(ServiceCatalog.FILE_IMPORTS, client_id=client, call_back=current_app.register_session) as service:
            file_importer = service.create(json_data=data)
            resp = make_response(schema, file_importer, 'File importer created!')
            return resp

    except Exception as e:
        return make_response(schema, None, 'Failed to create file importer!', error_msg=str(e), status_code=404)


@blueprint.route("/<client>/file_imports", methods=["GET"])
#@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_READ)
def get_file_importers(client):
    """
    :param client:
    :return: All the file importers that the client has
    """
    try:
        schema = FileImportersResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORTS, client_id=client, call_back=current_app.register_session) as service:
            file_importers = service.read()

            resp = make_response(schema, file_importers, 'File importers listed')
            return resp
    except ApiError as e:
        return make_response(schema, None, 'Failed to read file_importers', error_msg=e.message, status_code=400)


@blueprint.route('/<client>/file_imports/<int:id>', methods=['PATCH'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_UPDATE)
def update_file_importer(client, id):
    """

    :param
        - client:
        - file_parameter

    :return: Updates the file_importer from client with id file_importer.id
    """
    try:
        data = request.get_json()
        schema = FileImporterResponseSchema()

        with service_context(ServiceCatalog.FILE_IMPORTS, client_id=client, call_back=current_app.register_session) as service:
            file_importer = service.update(id, json_data=data)
            resp = make_response(schema, file_importer, 'File importer updated!')
            return resp

    except Exception as e:
        return make_response(schema, None, 'Failed to update file importer!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_imports/<id>', methods=['DELETE'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_DELETE)
def delete_file_importer(client, id):
    """

    :param
        - client:
        - file_parameter_id
    :return:
    """
    try:
        schema = FileImporterResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORTS, client_id=client, call_back=current_app.register_session) as service:
            file_importer = service.delete(int(id))
            resp = make_response(schema, file_importer, message=f"File importer with id {id} deleted!")
        return resp
    except Exception as e:
        return make_response(schema, None, 'Failed to delete file importer!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_imports/clone/<id>', methods=['POST'])
@permissions_requires_all(BuiltinPermission.FILE_IMPORTS_CREATE, BuiltinPermission.FILE_IMPORTS_READ)
def deep_copy_file_importer(client, id):
    try:
        schema = FileImporterResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORTS, client_id=client, call_back=current_app.register_session) as service:
            file_importer = service.deep_copy(int(id))
            return make_response(schema, file_importer, message=f"File importer with id {id} copied!")

    except Exception as e:
        return make_response(schema, None, 'Failed to copy file importer!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_imports/run/<id>', methods=['POST'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_READ)
def run_file_importer(client, id):
    try:
        with service_context(ServiceCatalog.FILE_IMPORTS, client_id=client, call_back=current_app.register_session) as service:
            file_importer = service.run_importer(int(id))
            return make_response(schema=None, response=None,
                                 message=f"Trigger to run importer with id {id} received succesfully!")

    except Exception as e:
        return make_response(schema=None, response=None, message='Failed to trigger the importer to run!',
                             error_msg=str(e), status_code=404)
