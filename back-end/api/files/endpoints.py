#  Copyright (c) 2015-2020 Condugo bvba

import json

from flask import request, current_app

from api.jwt_handlers import token_required
from api.v2.api_response import make_response
from api.v2.blueprint import blueprint
from cdg_service.catalog import ServiceCatalog
from cdg_service.errors import ApiError
from cdg_service.schemes.files import FileResponseSchema, FilesResponseSchema
from cdg_service.service_context import service_context
import sys

@blueprint.route('/<string:domain>/files', methods=['GET'])
@token_required()
def list_files(domain):
    """
    List all files for a domain.
    ---
    tags: ['Files']
    description: List all existing files.
    responses:
      200:
        description: Files successfully listed.
        schema:
          $ref: '#/definitions/FilesResponse'
      400:
        description: Failed to list files.
    """
    try:
        schema = FilesResponseSchema()
        extensions = request.args.get("extensions", "[]")
        exts = json.loads(extensions)
        with service_context(ServiceCatalog.FILE, client_id=domain, call_back=current_app.register_session) as service:
            files = service.read(extensions=exts)
            print(type(files), file=sys.stderr)
            resp = make_response(None, files, 'Files listed')

            return resp
    except ApiError as e:
        return make_response(schema, None, e.message, status_code=e.code)

@blueprint.route('/<string:domain>/files', methods=['POST'])
@token_required()
def upload_file(domain):
    """
    Upload file to a domain.
    ---
    tags: ['Files']
    description: List all existing files.
    responses:
      200:
        description: Files successfully listed.
        schema:
          $ref: '#/definitions/FilesResponse'
      400:
        description: Failed to list files.
    """
    try:
        f = request.files['file']
        # Validate file
        f.save(secure_filename(f.filename))
        return 'file uploaded successfully'


        schema = CreateFileSchema()
        extensions = request.args.get("extensions", "[]")
        exts = json.loads(extensions)
        with service_context(ServiceCatalog.FILE, client_id=domain, call_back=current_app.register_session) as service:
            files = service.read(extensions=exts)

            resp = make_response(schema, files, 'File uploaded')

            return resp
    except ApiError as e:
        return make_response(schema, None, e.message, status_code=e.code)


@blueprint.route('/<string:domain>/files/<string:filename>/analyse', methods=['GET'])
@token_required()
def analyse_file(domain, filename):
    """
    Analyse file with filename for a domain.
    ---
    tags: ['Files']
    description: Analyse file with filename for a domain.
    responses:
      200:
        description: File successfully analysed.
        schema:
          $ref: '#/definitions/FileResponse'
      400:
        description: Failed to analyse file.
    """
    try:
        schema = FileResponseSchema()
        with service_context(ServiceCatalog.FILE, client_id=domain, call_back=current_app.register_session) as service:
            file = service.analyse(filename)
            resp = make_response(None, file, 'File analysed!')

            return resp
    except ApiError as e:
        return make_response(schema, None, e.message, status_code=e.code)
