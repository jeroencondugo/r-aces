from flask import current_app

from api.access_decorators import permissions_requires_one
from api.v2 import blueprint, request
from api.v2.api_response import make_response
from cdg_service import ServiceCatalog
from cdg_service.errors import ApiError
from cdg_service.schemes.file_imports import FileImporterGlobResponseSchema, FileImporterGlobsResponseSchema
from cdg_service.service_context import service_context
from cdglib.models_general import BuiltinPermission


@blueprint.route("/<client>/file_import_globs", methods=["POST"])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_CREATE)
def create_importer_glob(client):
    try:
        data = request.get_json()
        schema = FileImporterGlobResponseSchema()

        with service_context(ServiceCatalog.FILE_IMPORT_GLOBS, client_id=client, call_back=current_app.register_session) as service:
            importer_glob = service.create(json_data=data)
            resp = make_response(schema, importer_glob, 'Importer glob created')
            return resp

    except Exception as e:
        return make_response(schema, None, 'Failed to create importer glob!', error_msg=str(e), status_code=404)


@blueprint.route("/<client>/file_import_globs", methods=["GET"])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_READ)
def get_importer_globs(client):
    """
    :param client:
    :return: All the importers globs that the client has
    """
    try:
        importer_id = request.args.get('importer_id')
        schema = FileImporterGlobsResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORT_GLOBS, client_id=client, call_back=current_app.register_session) as service:
            importer_globs = service.read(importer_id=importer_id)
            resp = make_response(schema, importer_globs, 'Importer globs listed')
            return resp
    except ApiError as e:
        return make_response(schema, None, 'Failed to read importer globs', error_msg=e.message, status_code=400)


@blueprint.route('/<client>/file_import_globs/<int:id>', methods=['PATCH'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_UPDATE)
def update_importer_glob(client, id):
    """

    :param
        - client:
        - importer_glob as json_data

    :return: Updates the updated importer glob
    """
    try:
        data = request.get_json()
        schema = FileImporterGlobResponseSchema()

        with service_context(ServiceCatalog.FILE_IMPORT_GLOBS, client_id=client, call_back=current_app.register_session) as service:
            importer_glob = service.update(id, json_data=data)
            resp = make_response(schema, importer_glob, 'Importer glob updated!')
        return resp

    except Exception as e:
        return make_response(schema, None, 'Failed to update importer glob!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_import_globs/<id>', methods=['DELETE'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_DELETE)
def delete_importer_glob(client, id):
    """

    :param
        - client:
        - importer_glob id
    :return:
    """
    try:
        schema = FileImporterGlobResponseSchema()
        with service_context(ServiceCatalog.FILE_IMPORT_GLOBS, client_id=client, call_back=current_app.register_session) as service:
            importer_glob = service.delete(int(id))
            return make_response(schema, importer_glob, message=f"Importer glob with id {id} deleted!")

    except Exception as e:
        return make_response(schema, None, 'Failed to importer glob!', error_msg=str(e), status_code=404)


@blueprint.route('/<client>/file_import_globs/test', methods=['POST'])
@permissions_requires_one(BuiltinPermission.FILE_IMPORTS_READ)
def test_importer_glob(client):
    try:
        data = request.get_json()
        with service_context(ServiceCatalog.FILE_IMPORT_GLOBS, client_id=client, call_back=current_app.register_session) as service:
            success = service.test(data)
            print(success)
            return make_response(None, success, message=f"Missed and matched globs sent")

    except Exception as e:
        return make_response(None, None, 'Failed to test importer globs!', error_msg=str(e), status_code=404)
