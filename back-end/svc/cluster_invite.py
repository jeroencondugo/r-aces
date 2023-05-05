from datetime import datetime, timedelta
from typing import Union, List

from sqlalchemy import or_

from cdg_service.errors import InvalidParameter
from cdg_service.schemes.cluster_invite import CreateClusterInviteSchema, UpdateClusterInviteSchema, InviteExpired
from cdg_service.service.basetree import BasetreeService
from cdg_service.service.common.base_service import Service
from cdg_service.service.graph_model import GraphModelService
from cdglib import scoped_domain_session
from cdglib.init_lib import app_config
from cdglib.models_general.security import Cluster, Client, ClusterInvite, ClientCluster, UserRole, User, Role, \
    Permission, Domain


class ClusterInviteService(Service):

    def __init__(self, session=None):
        super(ClusterInviteService, self).__init__(session)

    def create(self, json_data: dict, check_existing: bool = False) -> ClusterInvite:
        session = self.session
        serializer = CreateClusterInviteSchema()

        try:
            res = serializer.load(json_data, session=session)
            if res.errors:
                raise InvalidParameter("Invalid cluster invite param(s)")
        except ValueError as e:
            raise InvalidParameter(message="Invalid cluster invite param(s")

        invite = res.data

        if check_existing:
            if session.query(ClientCluster).filter(ClientCluster.client_id == invite.client_id,
                                                   ClientCluster.cluster_id == invite.cluster_id).first():
                raise InvalidParameter("Client already part of the cluster")
            elif session.query(ClusterInvite).filter(ClusterInvite.client_id == invite.client_id,
                                                     ClusterInvite.cluster_id == invite.cluster_id,
                                                     ClusterInvite.expired == False).first():
                raise InvalidParameter("Invite already exists")
        if not session.query(Client).get(invite.client_id):
            raise InvalidParameter("No such client")
        if not session.query(Cluster).get(invite.cluster_id):
            raise InvalidParameter("No such cluster")

        invite.accepted = None
        days_valid = json_data.get("days_valid", None)

        if days_valid:
            try:
                days_valid = int(days_valid)
                if 0 >= days_valid:
                    raise ValueError
                invite.expires_at = datetime.utcnow() + timedelta(days=days_valid)
            except ValueError:
                raise InvalidParameter("Days must be positive integer")
        session.add(invite)
        return invite

    def read(self, id_list: Union[int, list] = [], expired: InviteExpired = InviteExpired.BOTH, partial: bool = False,
             user_id: int = None, client_ids: Union[int, List[int]] = []) -> List[ClusterInvite]:
        if isinstance(id_list, int):
            id_list = [id_list]
        elif not all(isinstance(x, int) for x in id_list):
            raise InvalidParameter("List of passed ClusterInvite IDs contains not-integer value(s)")
        elif user_id and not isinstance(user_id, int):
            raise InvalidParameter("Passed user_id is not an integer")

        session = self.session
        query = session.query(ClusterInvite)
        if user_id:
            query = query. \
                join(Domain, or_(Domain.id == ClusterInvite.client_id, Domain.id == ClusterInvite.cluster_id)). \
                join(UserRole, UserRole.domain_id == Domain.id). \
                join(Role, Role.id == UserRole.role_id). \
                filter(UserRole.user_id == user_id, Permission.id.in_([Permission.CLUSTER_INVITE_READ]))

        opts = [ClusterInvite.expired == (expired == InviteExpired.YES)] if expired != InviteExpired.BOTH else []
        if client_ids:
            if not isinstance(client_ids, list):
                client_ids = [client_ids]

            opts.append(ClusterInvite.client_id.in_(client_ids))

        if id_list:
            opts.append(ClusterInvite.id.in_(id_list))
            loaded_invites = query.filter(*tuple(opts)).all()
            if not partial and len(loaded_invites) != len(id_list):
                raise InvalidParameter("Some of the cluster invites marked for read were not found")
        else:
            loaded_invites = query.filter(*tuple(opts)).all()

        if user_id:
            user_clients = set(c.id for c in session.query(Client).
                               join(UserRole, UserRole.domain_id == Client.id).
                               join(User, UserRole.user_id == User.id).
                               filter(UserRole.user_id == user_id, UserRole.domain_id is not None).all())

            for invite in loaded_invites:
                invite.received = invite.client_id in user_clients

        return loaded_invites

    def update(self, json_data, invite: ClusterInvite = None) -> ClusterInvite:
        if invite and not isinstance(invite, ClusterInvite):
            raise InvalidParameter("Wrong object passed for ClusterInvite")

        invite_id = json_data.get("id") or (invite.id if invite else None)
        if not invite_id:
            raise InvalidParameter("ClusterInvite ID is missing")

        if invite and invite.id != invite_id:
            raise InvalidParameter("ClusterInvite ID mismatch")

        session = self.session

        # try to load cluster invite from the DB if not already passed
        if not invite:
            invite = session.query(ClusterInvite).get(invite_id)
            if not invite:
                raise InvalidParameter("No such cluster invite found")

        if invite.expired:
            raise InvalidParameter("Invitation expired")
        elif "PENDING" != invite.status:
            raise InvalidParameter("Invitation can not be altered")

        serializer = UpdateClusterInviteSchema(strict=True)
        res = serializer.load(json_data, session=session, instance=invite)
        if res.errors:
            raise InvalidParameter("Invalid cluster invite param(s)")

        invite = res.data

        if invite.accepted:
            # Add client to the cluster
            session.add(
                ClientCluster(client_id=invite.client_id, cluster_id=invite.cluster_id, begin_utc=datetime.utcnow()))
            # Setup graph nodes in cluster model
            cluster = invite.cluster
            with scoped_domain_session(domain=cluster.schema) as cluster_session:
                # Find the first site
                bt_service = BasetreeService(session=cluster_session, config=app_config)
                sites_bt = bt_service.get_sites_basetree(include_nodes=True, include_levels=True)
                main_site = None
                for site in sites_bt.sites:
                    if site.name == cluster.name:
                        main_site = site
                        break

                gm_service = GraphModelService(session=cluster_session, config=app_config)
                client = invite.client
                try:
                    client_label = client.name[:10]
                except IndexError:
                    client_label = client.name
                payload = {
                    "added_groups": [],
                    "added_input_ports": [
                        # {
                        #     "id": "new_14",
                        #     "graph_node_id": "new_12",
                        #     "commodity_type": 5,
                        #     "meter_id": None
                        # }
                    ],
                    "added_nodes": [
                        {
                            "type": "GraphNodeSource",
                            "id": "new_9",
                            "name": client.name,
                            "label": client_label,
                            "grouping_id": main_site.id,
                            "ean_code": None,
                            "client_id": client.id,
                            "locked": True
                        },
                        {
                            "type": "GraphNodeSink",
                            "id": "new_12",
                            "name": client.name,
                            "label": client_label,
                            "grouping_id": main_site.id,
                            "client_id": client.id,
                            "locked": True
                        }
                    ],
                    "added_output_ports": [
                        # {
                        #     "id": "new_11",
                        #     "graph_node_id": "new_9",
                        #     "commodity_type": 5,
                        #     "meter_id": None,
                        #     "input_port_id": None,
                        #     "input_node_id": None,
                        #     "product_flow": False,
                        #     "value_weight": None
                        # }
                    ],
                    "added_ratios": [],
                    "deleted_groups": [],
                    "deleted_input_ports": [],
                    "deleted_nodes": [],
                    "deleted_output_ports": [],
                    "deleted_ratios": [],
                    "modified_groups": [],
                    "modified_input_ports": [],
                    "modified_nodes": [],
                    "modified_output_ports": [],
                    "modified_ratios": []
                }
                gm_service.apply_changeset(site_id=main_site.id, json_data=payload)

        session.add(invite)

        return invite

    def delete(self, id_list: Union[int, list], id_only: bool = False, partial=False) -> List[int]:
        if isinstance(id_list, int):
            id_list = [id_list]
        elif not all(isinstance(x, int) for x in id_list):
            raise InvalidParameter("List of passed ClusterInvite IDs contains not-integer value(s)")

        session = self.session

        loaded_cluster_invites = session.query(ClusterInvite).filter(ClusterInvite.id.in_(id_list)).all()
        if not partial and len(loaded_cluster_invites) != len(id_list):
            raise InvalidParameter("Some of the cluster invites marked for deletion were not found")

        deleted_invites = []
        for invite in loaded_cluster_invites:
            deleted_invites.append(invite.id if id_only else invite)
            session.delete(invite)

        return deleted_invites

    def accept(self, invite_id: int) -> ClusterInvite:
        """ Accept the invite to join the cluster. This will add the client to the cluster's associated clients list
            and create source and sink nodes in the cluster's graph model
        """

        return self.update(json_data={"id": invite_id, "accepted": True})

    def deny(self, invite_id: int) -> ClusterInvite:
        """ Denying the invite to join the cluster. This invite's state is updated """
        return self.update(json_data={"id": invite_id, "accepted": False})

    def revoke(self, invite_id: int) -> ClusterInvite:
        """ Revoke the invite. Before the invite is accepted or rejected the invite can be revoked. If an invite is
            already accepted, a termination procedure must be done
        """
        if not invite_id or not isinstance(invite_id, int):
            raise InvalidParameter("Wrong invite ID type")

        invite = self.session.query(ClusterInvite).get(invite_id)
        if not invite:
            raise InvalidParameter("No such invite found")
        if invite.status != "PENDING":
            raise InvalidParameter("Invite not in pending state")

        self.session.delete(invite)

        return invite
