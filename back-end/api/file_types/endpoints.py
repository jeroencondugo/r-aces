#  Copyright (c) 2015-2020 Condugo bvba

from flask import current_app

from api.jwt_handlers import token_required
from api.v2.api_response import make_response
from api.v2.blueprint import blueprint
from cdg_service.catalog import ServiceCatalog
from cdg_service.errors import ApiError
from cdg_service.schemes.files import FileTypesResponseSchema
from cdg_service.service_context import service_context


@blueprint.route("/gen/files/types", methods=["GET"])
@token_required()
def list_file_types():
    """
    List all file types for a domain.
    ---
    tags: ['Domain']
    description: List all existing file types.
    responses:
      200:
        description: Domains successfully listed.
        schema:
          $ref: '#/definitions/DomainsResponse'
      400:
        description: Failed to list domains.
    """
    try:
        schema = FileTypesResponseSchema()
        with service_context(ServiceCatalog.FILETYPE, call_back=current_app.register_session) as service:
            file_types = service.read()

            resp = make_response(schema, file_types, "File types listed")

            return resp
    except ApiError as e:
        return make_response(schema, None, e.message, status_code=e.code)
