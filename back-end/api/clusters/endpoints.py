#  Copyright (c) 2015-2021 Condugo bvba
from flask import g, request, current_app

from api.access_decorators import permissions_requires_one
from api.v2.api_response import make_response
from api.v2.blueprint import blueprint
from cdg_service import ServiceCatalog
from cdg_service.errors import ApiError
from cdg_service.schemes.cluster import ClusterResponseSchema, ClustersResponseSchema, ClustersDeletedResponseSchema, ClusterBansResponseSchema
from cdg_service.service.cluster import ClusterService
from cdg_service.service_context import service_context
from cdglib import scoped_general_session
from cdglib.models_general.security import Permission


@blueprint.route("/gen/cluster", methods=["POST"])
@permissions_requires_one(Permission.CLUSTER_CREATE)
def create_cluster():
    schema = ClusterResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterService(session=session, config=current_app.config)
            cluster = service.create(json_data=request.get_json(silent=True))

            response = make_response(schema, cluster, "Cluster created")
    except ApiError as e:
        response = make_response(schema, None, "Failed to create cluster", error_msg=e.message, status_code=e.code)

    return response


@blueprint.route("/gen/cluster", methods=["GET"])
@permissions_requires_one(Permission.CLUSTER_READ)
def read_clusters():
    schema = ClustersResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterService(session=session)
            cluster = service.read(read_deleted=False, user_id=g.current_identity)

            response = make_response(schema, cluster, "Clusters read")

    except Exception as e:
        response = make_response(schema, None, "Failed to read clusters", error_msg=str(e), status_code=404)

    return response


@blueprint.route("/gen/cluster/<int:cluster_id>", methods=["PATCH"])
@permissions_requires_one(Permission.CLUSTER_UPDATE)
def update_clusters(cluster_id):
    schema = ClusterResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterService(session)
            json_data = request.get_json(silent=True)
            json_data["id"] = cluster_id
            cluster = service.update(json_data=json_data)
            response = make_response(schema, cluster, "Cluster configuration updated")
    except ApiError as e:
        response = make_response(schema, None, "Failed to update cluster", error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, "Failed to update cluster", error_msg="Generic error", status_code=500)

    return response


@blueprint.route("/gen/cluster/<int:cluster_id>", methods=["DELETE"])
@permissions_requires_one(Permission.CLUSTER_DELETE)
def delete_cluster(cluster_id):
    schema = ClustersDeletedResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterService(session=session)
            cluster = service.delete(id_list=[cluster_id], partial=True)

            response = make_response(schema, cluster, "Cluster deleted")
    except ApiError as e:
        response = make_response(schema, None, "Failed to delete cluster", error_msg=e.message, status_code=e.code)

    return response


@blueprint.route("/gen/cluster/ban_clients/<int:cluster_id>", methods=["PATCH"])
@permissions_requires_one(Permission.CLUSTER_UPDATE)
def ban_clients(cluster_id):
    schema = ClusterBansResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterService(session)
            json_data = request.get_json(silent=True)
            reason = json_data.get("reason", "Not specified")
            client_ids = json_data.get("client_ids", [])
            bans = service.ban_clients(admin_id=g.current_identity, cluster_id=cluster_id, client_ids=client_ids, reason=reason).values()
            response = make_response(schema, bans, "Cluster client bans updated")
    except ApiError as e:
        response = make_response(schema, None, "Failed to ban cluster clients", error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, "Failed to ban cluster clients", error_msg="Generic error", status_code=500)

    return response


@blueprint.route("/gen/cluster/unban_clients/<int:cluster_id>", methods=["PATCH"])
@permissions_requires_one(Permission.CLUSTER_UPDATE)
def unban_clients(cluster_id):
    schema = ClusterBansResponseSchema()
    try:
        with scoped_general_session(call_back=current_app.register_session) as session:
            service = ClusterService(session)
            json_data = request.get_json(silent=True)
            reason = json_data.get("reason", "Not specified")
            client_ids = json_data.get("client_ids", [])
            bans = service.unban_clients(admin_id=g.current_identity, cluster_id=cluster_id, client_ids=client_ids, reason=reason).values()
            response = make_response(schema, bans, "Cluster client bans updated")
    except ApiError as e:
        response = make_response(schema, None, "Failed to unban cluster clients", error_msg=e.message, status_code=e.code)
    except Exception as e:
        response = make_response(schema, None, "Failed to unban cluster clients", error_msg="Generic error", status_code=500)

    return response
