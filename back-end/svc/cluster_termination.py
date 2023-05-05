from datetime import datetime, timedelta
from typing import List, Union, Optional

from flask import g
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from cdg_service.errors import InvalidParameter
from cdg_service.schemes.cluster_termination import CreateClusterTerminationSchema, UpdateClusterTerminationSchema, \
    TerminationExpired
from cdg_service.service.common.base_service import Service
from cdg_service.service.graph_model import GraphModelService
from cdg_service.service.graph_node import GraphNodeService
from cdglib import scoped_domain_session
from cdglib.init_lib import app_config
from cdglib.models_general.security import Cluster, Client, ClientCluster, ClusterMembershipTermination, UserRole, User, \
    ClusterInvite, Domain, Role, Permission


class ClusterTerminationService(Service):

    def __init__(self, session=None):
        super(ClusterTerminationService, self).__init__(session)

    def create(self, json_data: dict, check_existing: bool = False) -> ClusterMembershipTermination:
        session = self.session
        serializer = CreateClusterTerminationSchema()

        try:
            res = serializer.load(json_data, session=session)
            if res.errors:
                raise InvalidParameter("Invalid cluster termination param(s)")
        except ValueError as e:
            raise InvalidParameter(message="Invalid cluster termination param(s")

        termination = res.data

        if check_existing:
            if not session.query(ClientCluster).filter(ClientCluster.client_id == termination.client_id,
                                                       ClientCluster.cluster_id == termination.cluster_id).first():
                raise InvalidParameter("Client not part of the cluster")
            elif session.query(ClusterMembershipTermination).filter(
                    ClusterMembershipTermination.client_id == termination.client_id,
                    ClusterMembershipTermination.cluster_id == termination.cluster_id,
                    ClusterMembershipTermination.expired == False).first():
                raise InvalidParameter("Termination already exists")

        termination.accepted = None
        days_valid = json_data.get("days_valid", None)

        if days_valid:
            try:
                days_valid = int(days_valid)
                if 0 >= days_valid:
                    raise ValueError
            except ValueError:
                raise InvalidParameter("Days must be positive integer")
        elif not session.query(Client).get(termination.client_id):
            raise InvalidParameter("No such client")
        elif not session.query(Cluster).get(termination.cluster_id):
            raise InvalidParameter("No such cluster")

        if days_valid:
            termination.expires_at = datetime.utcnow() + timedelta(days=days_valid)

        session.add(termination)

        return termination

    def read(self, user: User, domain_id: int, id_list: Optional[Union[int, list]] = None,
             expired: Optional[TerminationExpired] = None, partial: bool = False) -> List[ClusterMembershipTermination]:
        if not domain_id or not user:
            return []
        if id_list and isinstance(id_list, int):
            id_list = [id_list]
        elif isinstance(id_list, list) and not all(isinstance(x, int) for x in id_list):
            raise InvalidParameter("List of passed ClusterMembershipTermination IDs contains not-integer value(s)")

        session = self.session
        query = session.query(ClusterMembershipTermination)
        opts = []
        user_is_condugo_admin = 1 in [role.id for role in user.roles]
        # if user is condugo admin all terminations are shown else only the ones for the current domain_id
        if not user_is_condugo_admin:
            opts.append(ClusterMembershipTermination.client_id==domain_id)
        if expired:
            opts.append(ClusterMembershipTermination.expired == (expired == TerminationExpired.YES))
        if id_list:
            opts.append(ClusterMembershipTermination.id.in_(id_list))
        if opts:
            query = query.filter(*tuple(opts))
        loaded_terminations = query.all()
        if loaded_terminations and id_list and not partial and len(loaded_terminations) != len(id_list):
            raise InvalidParameter("Some of the cluster terminations marked for read were not found")

        return loaded_terminations

    def update(self, json_data: dict, termination: ClusterMembershipTermination = None) -> ClusterMembershipTermination:
        if termination and not isinstance(termination, ClusterMembershipTermination):
            raise InvalidParameter("Wrong object passed for ClusterMembershipTermination")

        termination_id = json_data.get("id") or (termination.id if termination else None)
        if not termination_id:
            raise InvalidParameter("ClusterMembershipTermination ID is missing")

        if termination and termination.id != termination_id:
            raise InvalidParameter("ClusterMembershipTermination ID mismatch")

        session = self.session

        # try to load cluster termination from the DB if not already passed
        if not termination:
            termination = session.query(ClusterMembershipTermination).get(termination_id)
            if not termination:
                raise InvalidParameter("No such cluster termination found")

        if termination.expired:
            raise InvalidParameter("Termination expired")
        elif "PENDING" != termination.status:
            raise InvalidParameter("Termination can not be altered")

        serializer = UpdateClusterTerminationSchema(strict=True)
        res = serializer.load(json_data, session=session, instance=termination)
        if res.errors:
            raise InvalidParameter("Invalid cluster termination param(s)")

        termination = res.data

        if termination.accepted:
            # mark end of membership in the ClientCluster entry
            cc = session.query(ClientCluster).filter(ClientCluster.client_id == termination.client_id,
                                                     ClientCluster.cluster_id == termination.cluster_id).first()
            if not cc:
                raise InvalidParameter("No ClientCluster found")

            cc.end_utc = datetime.utcnow()
            session.add(cc)
            # Remove source and sink graph nodes from cluster graph model
            # Setup graph nodes in cluster model
            cluster = termination.cluster
            client = termination.client
            self._set_classmap_domain_type(cluster.schema)
            with scoped_domain_session(domain=cluster.schema) as cluster_session:
                GraphNode = self._classmap.GraphNode
                #nodes = cluster_session.query(GraphNode).filter(GraphNode.client_id == client.id)
                gm_service = GraphModelService(session=cluster_session, config=app_config)
                nodes = gm_service.read(client_id=client.id)
                node_ids = []
                iport_ids = []
                oport_ids = []
                ratio_ids = []
                node: GraphNode
                for node in nodes:
                    node_ids.append(node.id)
                    for iport in node.input_ports:
                        iport_ids.append(iport.id)
                    for oport in node.output_ports:
                        oport_ids.append(oport.id)
                    if node.discriminator == 'graph_node_converter':
                        for ratio in node.ratios:
                            ratio_ids.append(ratio.id)
                gm_service.delete_ratios(ratio_ids)
                gm_service.delete_input_ports(iport_ids)
                gm_service.delete_output_ports(oport_ids)
                gm_service.delete_nodes(node_ids)

            session.add(termination)

        return termination

    def delete(self, id_list: Union[int, list], id_only: bool = False, partial=False) -> List[int]:
        if isinstance(id_list, int):
            id_list = [id_list]
        elif not all(isinstance(x, int) for x in id_list):
            raise InvalidParameter("List of passed ClusterMembershipTermination IDs contains not-integer value(s)")

        session = self.session

        loaded_cluster_terminations = session.query(ClusterMembershipTermination).filter(
            ClusterMembershipTermination.id.in_(id_list)).all()
        if not partial and len(loaded_cluster_terminations) != len(id_list):
            raise InvalidParameter("Some of the cluster terminations marked for deletion were not found")

        deleted_terminations = []
        for termination in loaded_cluster_terminations:
            deleted_terminations.append(termination.id if id_only else termination)
            session.delete(termination)

        return deleted_terminations

    def accept(self, termination_id: int) -> ClusterMembershipTermination:
        return self.update(json_data={"id": termination_id, "accepted": True})

    def deny(self, termination_id: int) -> ClusterMembershipTermination:
        return self.update(json_data={"id": termination_id, "accepted": False})

    def revoke(self, termination_id: int) -> ClusterMembershipTermination:
        if not termination_id or not isinstance(termination_id, int):
            raise InvalidParameter("Wrong termination ID type")

        termination = self.session.query(ClusterMembershipTermination).get(termination_id)
        if not termination:
            raise InvalidParameter("No such termination found")
        elif termination.status != "PENDING":
            raise InvalidParameter("Termination not in pending state")

        self.session.delete(termination)

        return termination
