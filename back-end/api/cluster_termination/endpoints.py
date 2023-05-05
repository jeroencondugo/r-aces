#  Copyright (c) 2015-2020 Condugo bvba

from flask import g, request, current_app

from api.access_decorators import permissions_requires_one
from api.v2.api_response import make_response
from api.v2.blueprint import blueprint
from cdg_service.errors import ApiError
from cdg_service.schemes.cluster_termination import ClusterTerminationResponseSchema, ClusterTerminationsResponseSchema, \
    TerminationExpired
from cdg_service.service.cluster_termination import ClusterTerminationService
from cdglib import scoped_general_session
from cdglib.models_general import Permission


@blueprint.route('/gen/cluster_terminations', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_CREATE)
def create_cluster_termination():
    schema = ClusterTerminationsResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            json_data = request.get_json(silent=True)
            if not isinstance(json_data, list):
                json_data = [json_data]

            terminations = []
            for jd in json_data:
                terminations.append(service.create(json_data=jd, check_existing=True))

            session.flush()
            response = make_response(schema, terminations, 'Cluster termination(s) created')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to create cluster termination', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, 'Failed to create cluster termination', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_terminations', methods=['GET'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_READ)
def read_cluster_terminations():
    # """
    # List clusters
    # ---
    # tags: ['Cluster Management (v2)']
    # description: List meter values.
    # parameters:
    # responses:
    #   200:
    #     description: Cluster(s) listed.
    #     schema:
    #       $ref: '#/definitions/ClustersResponse'
    #   400:
    #     description: Cluster(s) not found.
    # """
    schema = ClusterTerminationsResponseSchema()
    try:
        domain_id = request.args.get('domain_id')
        if not domain_id:
            return make_response(None, [], error_msg='domain_id argument required', status_code=400)
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            expired_arg = request.args.get("expired")
            expired = TerminationExpired[expired_arg.upper()] if expired_arg else None
            terminations = service.read(expired=expired, user=g.user, domain_id=domain_id)
            response = make_response(schema, terminations, 'Cluster terminations read')
        return response

    except Exception as e:
        return make_response(schema, None, 'Failed to read cluster terminations', error_msg=str(e), status_code=404)


@blueprint.route('/gen/cluster_terminations/<int:termination_id>', methods=['PATCH'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_UPDATE)
def update_cluster_termination(termination_id):
    schema = ClusterTerminationResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            termination = service.update(termination_id, request.get_json(silent=True))
            response = make_response(schema, termination, 'Cluster termination updated')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to update cluster termination', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, 'Failed to update cluster termination', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_terminations/<int:termination_id>', methods=['DELETE'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_DELETE)
def delete_cluster_termination(termination_id):
    # """
    # Delete meter with id.
    # ---
    # tags: ['Client Management']
    # description: Delete  client with id.
    # parameters:
    #   - name: id
    #     in: path
    #     type: integer
    #     required: true
    #     description: ID of the client
    # responses:
    #   200:
    #     description: Client has been deleted.
    #     schema:
    #       $ref: '#/definitions/ClientResponse'
    #   404:
    #     description: Client not found.
    # """
    schema = ClusterTerminationsResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            terminations = service.delete(id_list=termination_id)
            response = make_response(schema, terminations, 'Cluster termination deleted')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to delete cluster termination', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to delete cluster termination', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_terminations/accept/<int:termination_id>', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_UPDATE)
def accept_cluster_termination(termination_id):
    # """
    # Delete meter with id.
    # ---
    # tags: ['Client Management']
    # description: Delete  client with id.
    # parameters:
    #   - name: id
    #     in: path
    #     type: integer
    #     required: true
    #     description: ID of the client
    # responses:
    #   200:
    #     description: Client has been deleted.
    #     schema:
    #       $ref: '#/definitions/ClientResponse'
    #   404:
    #     description: Client not found.
    # """
    schema = ClusterTerminationResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            termination = service.accept(termination_id=termination_id)
            response = make_response(schema, termination, 'Cluster termination accepted')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to accept cluster termination', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to accept cluster termination', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_terminations/deny/<int:termination_id>', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_UPDATE)
def deny_cluster_termination(termination_id):
    # """
    # Delete meter with id.
    # ---
    # tags: ['Client Management']
    # description: Delete  client with id.
    # parameters:
    #   - name: id
    #     in: path
    #     type: integer
    #     required: true
    #     description: ID of the client
    # responses:
    #   200:
    #     description: Client has been deleted.
    #     schema:
    #       $ref: '#/definitions/ClientResponse'
    #   404:
    #     description: Client not found.
    # """
    schema = ClusterTerminationResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            termination = service.deny(termination_id=termination_id)
            response = make_response(schema, termination, 'Cluster termination denied')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to deny cluster termination', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, 'Failed to deny cluster termination', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_terminations/revoke/<int:cluster_id>/<int:client_id>', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_TERMINATE_DELETE)
def revoke_cluster_termination(cluster_id, client_id):
    # """
    # Delete meter with id.
    # ---
    # tags: ['Client Management']
    # description: Delete  client with id.
    # parameters:
    #   - name: id
    #     in: path
    #     type: integer
    #     required: true
    #     description: ID of the client
    # responses:
    #   200:
    #     description: Client has been deleted.
    #     schema:
    #       $ref: '#/definitions/ClientResponse'
    #   404:
    #     description: Client not found.
    # """
    schema = ClusterTerminationResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterTerminationService(session)
            invite = service.revoke(cluster_id, client_id)
            response = make_response(schema, invite, 'Cluster termination revoked')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to revoke cluster termination', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to revoke cluster termination', error_msg='Generic error', status_code=500)

    return response
