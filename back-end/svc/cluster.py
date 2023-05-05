import dataclasses
from collections import defaultdict
from datetime import datetime
from typing import Union, List, Dict
import os
from flask import current_app

from cdg_service.errors import InvalidParameter
from cdg_service.schemes import CreateClusterSchema, UpdateClusterSchema
from cdg_service.service.basetree import BasetreeService
from cdg_service.service.basetree_level import BasetreeLevelService
from cdg_service.service.basetree_node import BasetreeNodeService
from cdg_service.service.common.base_service import Service
from cdg_service.service.common.influx_buckets import create_influx2_buckets, drop_influx2_buckets
from cdg_service.service.database import DbService
from cdglib import scoped_domain_session
from cdglib.cryptography import Cryptography
from cdglib.database import ClusterBase
from cdglib.factories import scoped_common_data_session
from cdglib.influx import influxdb_session
from cdglib.influx.client import InfluxClient
from cdglib.init_lib import get_app_config
from cdglib.models_cluster import Organisation, GraphModel
from cdglib.models_general.security import Cluster, User, Ban, Client, UserRole, Role, RolePermission, Permission, \
    Domain


class ClusterService(Service):

    def __init__(self, session=None, config=None):
        super(ClusterService, self).__init__(session, config=config)

    def check_schema(self, schema):
        clusters = self.session.query(Cluster).all()
        used_schemas = [c.schema for c in clusters]
        if schema in used_schemas:
            return False
        else:
            return True

    def create(self, json_data: dict = {}) -> Cluster:
        session = self.session
        serializer = CreateClusterSchema()

        try:
            cluster = Cluster()
            res = serializer.load(json_data, session=session, instance=cluster)
            if res.errors:
                raise InvalidParameter("Invalid cluster param(s)")
        except ValueError as e:
            raise InvalidParameter(message="Invalid cluster param(s")

        cluster = res.data

        if not cluster.name:
            raise InvalidParameter("Invalid cluster param(s)")
        elif session.query(Cluster).filter(Cluster.name == cluster.name).first():
            raise InvalidParameter("Cluster with such name already exists")

        cluster.reinit()

        # check if schema is unique, if not regenerate
        while not self.check_schema(cluster.schema):
            proposed_schema = 'cl_{}'.format(cluster._generate_random_schema())
            cluster.schema = proposed_schema

        given_password = json_data.get("schema_password")
        if given_password:
            cluster.schema_password = Cryptography.encrypt(data=given_password, seed=cluster._seed())
        else:
            cluster.schema_password = Cryptography.generate_encrypted_random_password(seed=cluster._seed())

        # TODO: maybe move this to schema? It did not add cluster-user relationship objects for some reason
        role_users = defaultdict(list)
        for ur in json_data.get('user_roles', []):
            role_users[ur["role_id"]].append(ur["user_id"])

        for role, users in role_users.items():
            cluster.add_users(role_id=role, users=users)

        db_svc = DbService()
        cfg = get_app_config()
        pg_config = cfg.pg_config
        try:
            db_svc.create_postgres_role(name=cluster.schema_user, password=cluster.cleartext_schema_password(),
                                        admin_uri=pg_config.uri)
            db_svc.create_postgres_schema(name=cluster.schema, owner=pg_config.username, db_name=pg_config.name,
                                          db_uri=pg_config.uri)

            # create influx objects
            create_influx2_buckets(cluster)

            with scoped_domain_session(domain=cluster.schema) as domain_session:
                ClusterBase.metadata.create_all(bind=domain_session.get_bind())

                base_path = self._config['DATA_BASE_PATH'] if self._config else "/etc/condugo"
                org = Organisation(name=cluster.name, schema=cluster.schema, base_path=f"{base_path}/{cluster.schema}")
                domain_session.add(org)

                gm = GraphModel()
                domain_session.add(gm)

                domain_session.commit()

                bt_service = BasetreeService(session=domain_session)
                btl_service = BasetreeLevelService(session=domain_session)
                btn_service = BasetreeNodeService(config=cfg, session=domain_session)

                commodity_type_bt = {
                    "name": "Commodity types",
                    "label": "CTS",
                    "bt_type": "commodity_type",
                    "locked": True,
                    "add_level_locked": True
                }
                bt_ct = bt_service.create(commodity_type_bt)

                geo_bt_dict = {
                    "name": "Sites",
                    "label": "SITE",
                    "bt_type": "company_sites",
                    "locked": True,
                    "add_level_locked": True
                }
                geo_bt = bt_service.create(geo_bt_dict)

                ct_bt_level = {
                    "basetree": bt_ct.id,
                    "name": "Commodity types",
                    "depth": 1,
                    "locked": True,
                    "type": "commodity_type",
                    "color": "#B2DF8A"
                }
                ct_bt = btl_service.create(ct_bt_level)

                sites_bt_level = {
                    "basetree": geo_bt.id,
                    "name": "Sites",
                    "depth": 1,
                    "locked": True,
                    "type": "sites",
                }
                sites_level = btl_service.create(sites_bt_level)
                # Create a default site with the name of the cluster
                root_node = geo_bt.get_root()
                default_site = {
                    "parent_id": root_node.id,
                    "type": "Node",
                    "name": cluster.name,
                    "label": "default",
                    "depth": 1,
                    "locked": True,
                }
                site = btn_service.create(default_site)

                with scoped_common_data_session() as cd_session:
                    btn_service.create_builtin_commodity_types(common_data_session=cd_session)

            session.add(cluster)
            session.commit()
        except Exception as e:
            try:
                db_svc.drop_postgres_schema(name=cluster.schema, db_name=cfg.pg_config.name)
            except:
                pass

            try:
                db_svc.drop_postgres_role(name=cluster.schema_user)
            except:
                pass

            raise

        return cluster

    def read(self, id_list: Union[int, list] = [], partial: bool = False, read_deleted: bool = True,
             user_id: int = None) -> List[Cluster]:
        if isinstance(id_list, int):
            id_list = [id_list]
        elif not all(isinstance(x, int) for x in id_list):
            raise InvalidParameter("List of passed Cluster IDs contains not-integer value(s)")

        session = self.session

        opts = []
        if not read_deleted:
            opts.append(Cluster.deleted == False)

        query = session.query(Cluster)

        if user_id:
            # if user is not Condugo admin, show only clusters on which it has CLUSTER_READ permission
            user_roles = set(r[0] for r in session.query(Role.id).
                             join(UserRole, UserRole.role_id == Role.id).
                             join(User, User.id == UserRole.user_id).
                             filter(User.id == user_id).all())

            if Role.CONDUGO_ADMIN not in user_roles:
                query = query.join(UserRole, UserRole.domain_id == Cluster.id). \
                    join(Role, Role.id == UserRole.role_id). \
                    join(RolePermission, RolePermission.role_id == Role.id). \
                    join(Permission, Permission.id == RolePermission.permission_id). \
                    filter(UserRole.user_id == user_id, Permission.id.in_([Permission.CLUSTER_READ]))

        if id_list:
            opts.append(Cluster.id.in_(id_list))
            loaded_clusters = query.filter(*tuple(opts)).all()
            if not partial and len(loaded_clusters) != len(id_list):
                raise InvalidParameter("Some of the clusters marked for read were not found")
        else:
            loaded_clusters = query.filter(*tuple(opts)).all()

        return loaded_clusters

    def update(self, json_data, cluster: Cluster = None) -> Cluster:
        if cluster and not isinstance(cluster, Cluster):
            raise InvalidParameter("Wrong object passed for Cluster")

        cluster_id = json_data.get("id") or (cluster.id if cluster else None)
        if not cluster_id:
            raise InvalidParameter("Cluster ID is missing")

        if cluster and cluster.id != cluster_id:
            raise InvalidParameter("Cluster ID mismatch")

        session = self.session

        # try to load cluster from the DB is not already passed
        if not cluster:
            cluster = session.query(Cluster).get(cluster_id)
            if not cluster:
                raise InvalidParameter("No such cluster found")

        if cluster.deleted:
            raise InvalidParameter("Cluster is marked for deletion")

        old_owner = cluster.schema_user

        serializer = UpdateClusterSchema()
        res = serializer.load(json_data, session=session, instance=cluster)
        if res.errors:
            raise InvalidParameter('Invalid cluster param(s)')

        cluster = res.data

        # TODO: maybe move this to schema? It did not add cluster-user relationship objects for some reason
        role_users = defaultdict(list)
        for ur in json_data.get('user_roles', []):
            role_users[ur["role_id"]].append(ur["user_id"])

        for role, users in role_users.items():
            cluster.add_users(role_id=role, users=users)

        if cluster.schema_user != old_owner:
            db_svc = DbService()
            cfg = get_app_config()

            cluster.schema_password = Cryptography.encrypt(data=cluster.schema_password, seed=cluster._seed())

            db_svc.create_postgres_role(name=cluster.schema_user, password=cluster.cleartext_schema_password())
            db_svc.set_postgres_schema_owner(name=cluster.schema, db_name=cfg.pg_config.name, owner=cluster.schema_user)

        session.add(cluster)

        return cluster

    def delete(self, id_list: Union[int, list], partial=False) -> list:
        if isinstance(id_list, int):
            id_list = [id_list]
        elif not all(isinstance(x, int) for x in id_list):
            raise InvalidParameter("List of passed Cluster IDs contains not-integer value(s)")

        session = self.session

        loaded_clusters = session.query(Cluster).filter(Cluster.id.in_(id_list)).all()
        if not partial and len(loaded_clusters) != len(id_list):
            raise InvalidParameter("Some of the clusters marked for deletion were not found")

        db_svc = DbService()
        cfg = get_app_config()
        pg_config = cfg.pg_config

        for cluster in loaded_clusters:
            drop_influx2_buckets(cluster)

        deleted_ids = []
        for cluster in loaded_clusters:
            deleted_ids.append(cluster.id)
            session.delete(cluster)

            try:
                db_svc.drop_postgres_schema(name=cluster.schema, db_name=pg_config.name, db_uri=pg_config.uri)
            except Exception as e:
                self.logger.error(e)
                pass

            try:
                db_svc.drop_postgres_role(name=cluster.schema_user, admin_uri=pg_config.uri)
            except Exception as e:
                self.logger.error(e)
                pass

        return deleted_ids

    def ban_clients(self, admin_id: int, cluster_id: int, client_ids: Union[int, List[int]],
                    reason: str = "Not specified") -> Dict[int, Ban]:
        if not admin_id or not isinstance(admin_id, int):
            raise InvalidParameter(f"admin_id is not an integer value: {admin_id}")
        elif not cluster_id or not isinstance(cluster_id, int):
            raise InvalidParameter(f"cluster_id is not an integer value: {cluster_id}")

        session = self.session
        if not session.query(User).get(admin_id):
            raise InvalidParameter(f"No such user found: {admin_id}")

        cluster = session.query(Cluster).get(cluster_id)
        if not cluster:
            raise InvalidParameter(f"No such cluster found: {cluster_id}")

        if not isinstance(client_ids, list):
            client_ids = [client_ids]

        # filter existing clients
        client_ids = set(c[0] for c in session.query(Client.id).filter(Client.id.in_(client_ids)).all())

        # find new bans. use map to convert subject to int, since its stored as string in JSONB
        bans = cluster.bans
        new_bans = client_ids - set(map(int, bans.keys()))

        # add  new bans
        timestamp = datetime.utcnow().isoformat()
        for client_id in new_bans:
            bans[client_id] = dataclasses.asdict(
                Ban(subject=client_id, issuer=admin_id, timestamp=timestamp, reason=reason))

        return {int(k): v for k, v in bans.items()}

    def unban_clients(self, admin_id: int, cluster_id: int, client_ids: Union[int, List[int]],
                      reason: str = "Not specified") -> Dict[int, Ban]:
        if not admin_id or not isinstance(admin_id, int):
            raise InvalidParameter(f"admin_id is not an integer value: {admin_id}")
        elif not cluster_id or not isinstance(cluster_id, int):
            raise InvalidParameter(f"cluster_id is not an integer value: {cluster_id}")

        session = self.session
        if not session.query(User).get(admin_id):
            raise InvalidParameter(f"No such user found: {admin_id}")

        cluster = session.query(Cluster).get(cluster_id)
        if not cluster:
            raise InvalidParameter(f"No such cluster found: {cluster_id}")

        if not isinstance(client_ids, list):
            client_ids = set([client_ids])
        else:
            client_ids = set(client_ids)

        # remove bans. use map to convert subject to str, since its stored as string in JSONB
        bans = cluster.bans
        for client_id in set(map(str, client_ids)):
            bans.pop(client_id, None)

        return {int(k): v for k, v in bans.items()}

