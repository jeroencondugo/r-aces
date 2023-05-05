#  Copyright (c) 2015-2020 Condugo bvba

from flask import g, request, current_app

from api.access_decorators import permissions_requires_one
from api.v2.api_response import make_response
from api.v2.blueprint import blueprint
from cdg_service.errors import ApiError, InvalidParameter
from cdg_service.schemes.cluster_invite import ClusterInviteResponseSchema, ClusterInvitesResponseSchema, InviteExpired
from cdg_service.service.cluster_invite import ClusterInviteService
from cdglib import scoped_general_session
from cdglib.models_general import Permission


@blueprint.route('/gen/cluster_invites', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_INVITE_CREATE)
def create_cluster_invite():
    schema = ClusterInvitesResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            json_data = request.get_json(silent=True)
            if not isinstance(json_data, list):
                json_data = [json_data]

            invites = []
            for jd in json_data:
                try:
                    inv = service.create(json_data=jd, check_existing=True)
                except InvalidParameter as e:
                    inv = None
                if inv: invites.append(inv)

            session.flush()
            response = make_response(schema, invites, 'Cluster invite(s) created')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to create cluster invite', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, 'Failed to create cluster invite', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_invites', methods=['GET'])
@permissions_requires_one(Permission.CLUSTER_INVITE_READ)
def read_cluster_invites():
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
    schema = ClusterInvitesResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            expired = InviteExpired[request.args.get("expired", "both").upper()]
            user_id = g.current_identity
            invites = service.read(expired=expired, user_id=user_id)
            response = make_response(schema, invites, 'Cluster invites read')
        return response
    except ApiError as e:
        return make_response(schema, None, e.message, status_code=e.code)
    except Exception as e:
        return make_response(schema, None, 'Failed to read cluster invites', error_msg=str(e), status_code=404)


@blueprint.route('/gen/cluster_invites/<int:invite_id>', methods=['PATCH'])
@permissions_requires_one(Permission.CLUSTER_INVITE_UPDATE)
def update_cluster_invite(invite_id):
    schema = ClusterInviteResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            invite = service.update(invite_id, request.get_json(silent=True))
            response = make_response(schema, invite, 'Cluster invite updated')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to update cluster invite', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, 'Failed to update cluster invite', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_invites/<int:invite_id>', methods=['DELETE'])
@permissions_requires_one(Permission.CLUSTER_INVITE_DELETE)
def delete_cluster_invite(invite_id):
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
    schema = ClusterInvitesResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            invites = service.delete(id_list=invite_id)
            response = make_response(schema, invites, 'Cluster invite deleted')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to delete cluster invite', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to delete cluster invite', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_invites/accept/<int:invite_id>', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_INVITE_UPDATE)
def accept_cluster_invite(invite_id):
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
    schema = ClusterInviteResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            invite = service.accept(invite_id=invite_id)
            response = make_response(schema, invite, 'Cluster invite accepted')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to accept cluster invite', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to accept cluster invite', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_invites/deny/<int:invite_id>', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_INVITE_UPDATE)
def deny_cluster_invite(invite_id):
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
    schema = ClusterInviteResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            invite = service.deny(invite_id=invite_id)
            response = make_response(schema, invite, 'Cluster invite denied')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to deny cluster invite', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to deny cluster invite', error_msg='Generic error', status_code=500)

    return response


@blueprint.route('/gen/cluster_invites/revoke/<int:cluster_id>/<int:client_id>', methods=['POST'])
@permissions_requires_one(Permission.CLUSTER_INVITE_DELETE)
def revoke_cluster_invite(cluster_id, client_id):
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
    schema = ClusterInviteResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterInviteService(session)
            invite = service.revoke(cluster_id, client_id)
            response = make_response(schema, invite, 'Cluster invite revoked')
    except ApiError as e:
        response = make_response(schema, None, 'Failed to revoke cluster invite', error_msg=e.message, status_code=e.code)
    except Exception as e:
        response =  make_response(schema, None, 'Failed to revoke cluster invite', error_msg='Generic error', status_code=500)

    return response
