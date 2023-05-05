from flask import current_app

from api.access_decorators import permissions_requires_one, permissions_requires_all
from api.v2 import blueprint, request
from api.v2.api_response import make_response
from cdg_service import ServiceCatalog
from cdg_service.errors import ApiError
from cdg_service.schemes.file_imports import FileImporterOptionsResponseSchema, FileImporterOptionResponseSchema
from cdg_service.service_context import service_context
from cdglib.models_general import BuiltinPermission


@blueprint.route("/<client>/file_import_options", methods=["POST"])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_CREATE)
def create_file_import_options(client):
    try:
        data = request.get_json()
        schema = FileImporterOptionResponseSchema()

        with service_context(ServiceCatalog.FILE_IMPORT_OPTIONS, client_id=client, call_back=current_app.register_session) as service:
            options = service.create(json_data=data)
            resp = make_response(schema, options, 'FileImporterOptions created!', status_code=201)
        return resp

    except Exception as e:
        return make_response(schema, None, 'Failed to create FileImporterOptions!!', error_msg=str(e), status_code=404)


@blueprint.route("/<client>/file_import_options", methods=["GET"])
#@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_READ)
def get_file_import_options(client):
    """
    :param client:
    :return: All the file importer optinos that the client has
    """
    try:
        importer_id = request.args.get('importer_id')
        schema = FileImporterOptionsResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORT_OPTIONS, client_id=client, call_back=current_app.register_session) as service:
            options = service.read(importer_id=importer_id)
            resp = make_response(schema, options, 'File importers options listed')
            return resp
    except ApiError as e:
        return make_response(schema, None, 'Failed to read file_importers_options', error_msg=e.message,
                             status_code=400)


@blueprint.route('/<client>/file_import_options/<int:id>', methods=['PATCH'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_UPDATE)
def update_file_import_options(client, id):
    """

    :param
        - client:
        - file_importer_options with id

    :return: Updates the file_importer from client with id file_importer.id
    """
    try:
        data = request.get_json()
        schema = FileImporterOptionResponseSchema()

        with service_context(ServiceCatalog.FILE_IMPORT_OPTIONS, client_id=client, call_back=current_app.register_session) as service:
            options = service.update(id, json_data=data)
            resp = make_response(schema, options, 'File importer options updated!')
        return resp

    except Exception as e:
        return make_response(schema, None, 'Failed to update file importer options!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_import_options/<id>', methods=['DELETE'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_DELETE)
def delete_file_importer_options(client, id):
    """

    :param
        - client:
        - file_parameter_id
    :return:
    """
    try:
        schema = FileImporterOptionResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORT_OPTIONS, client_id=client, call_back=current_app.register_session) as service:
            options = service.delete(int(id))
            resp = make_response(schema, options, f"File importer options with id {id} deleted!")
            service.session.commit()
            return resp
    except Exception as e:
        return make_response(schema, None, 'Failed to delete file importer options!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_import_options/clone/<id>', methods=['POST'])
@permissions_requires_all(BuiltinPermission.FILE_IMPORTS_CREATE, BuiltinPermission.FILE_IMPORTS_READ)
def copy_file_importer_options(client, id):
    try:
        schema = FileImporterOptionResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORT_OPTIONS, client_id=client, call_back=current_app.register_session) as service:
            options = service.copy(int(id))
            return make_response(schema, options, message=f"File importer options with id {id} copied!")

    except Exception as e:
        return make_response(schema, None, 'Failed to copy file importer!', error_msg=str(e), status_code=404)
