#  Copyright (c) 2015-2020 Condugo bvba

from api.v2.users.endpoints import login, logout
from flask import request
from .blueprint import blueprint
from .api_response import make_response
from api.v2.meters.endpoints import apply_changeset
from api.v2.meter_configs.endpoints import meter_configs, delete_meter_config, create_meter_config, update_meter_config, connect_port, meter_config_types

from api.v2.insights.endpoints import list_insights, save_insight, create_insight, delete_insight, patch_insight, reorder_insights, request_edit_insight, cancel_edit_insight
from api.v2.insight_level.endpoints import list_insight_level, list_insight_levels, create_insight_level, delete_insight_level, reorder_insight_levels, edit_insight_level
from api.v2.organisation.endpoints import list_organisation, list_organisations
from api.v2.clients.endpoints import create_client, read_clients, update_client, delete_client
from api.v2.clusters.endpoints import create_cluster, read_clusters
from api.v2.constants.endpoints import create_constant, read_constants, update_constant, delete_constant
from api.v2.domain.endpoints import list_domains, list_user_domains
from api.v2.permissions.endpoints import read_permissions
from api.v2.users.endpoints import login, logout, refresh_token, validate_token, list_user_permissions, read_users, create_user, edit_user, delete_user, add_users_roles, remove_users_roles
from api.v2.cluster_invites.endpoints import create_cluster_invite, read_cluster_invites, update_cluster_invite, delete_cluster_invite, accept_cluster_invite, deny_cluster_invite
from api.v2.cluster_termination.endpoints import create_cluster_termination, read_cluster_terminations, update_cluster_termination, delete_cluster_termination, accept_cluster_termination, deny_cluster_termination
from api.v2.roles.endpoints import list_roles, add_roles_permissions, remove_roles_permissions
from api.v2.sankey.endpoints import get_sankey_nodes, get_sankey_node_details, get_sankey_config
from api.v2.basetree_nodes.endpoints import list_nodes, create_node, edit_node, delete_node
from api.v2.basetrees.endpoints import list_site_hierarchies, list_site_hierarchy, create_site_hierachy, delete_site_hierarchy, patch_site_hierarchy, reorder_basetrees
from api.v2.basetree_levels.endpoints import list_basetree_levels, read_basetree_level, create_level, delete_level
from api.v2.graph_model.graph_node import save_graph_model_changes, get_graph_model, calculate_graph_model
from api.v2.meters.endpoints import read_meter, create_meter, delete_meter, update_meter
from api.v2.settings.endpoints import list_settings, create_settings, patch_settings, delete_setting, patch_settings_values, get_settings_values
from api.v2.cost_model.endpoints import list_cost_models, create_cost_model, patch_cost_model, delete_cost_model
from api.v2.pint.endpoints import read_dimensions, validate_unit
from api.v2.reports.report_view import *
from api.v2.files.endpoints import list_files, analyse_file
from api.v2.file_types.endpoints import list_file_types
from api.v2.historians.endpoints import create_historian, read_historians, update_historian, delete_historian, index_historian
from api.v2.commodity_type_templates.endpoints import list_ct_templates, get_ct_template, create_ct_template
from api.v2.timezones.endpoints import  list_all_time_zones
from api.v2.graph_model.graph_template import  list_graph_templates, create_graph_templates, delete_graph_templates
from api.v2.file_imports.endpoints import get_file_importers, update_file_importer, delete_file_importer, deep_copy_file_importer, run_file_importer
from api.v2.file_import_globs.endpoints import create_importer_glob, get_importer_globs, update_importer_glob, delete_importer_glob, test_importer_glob
from api.v2.file_import_options.endpoints import create_file_import_options,get_file_import_options, update_file_import_options, delete_file_importer_options, copy_file_importer_options
from api.v2.meter_models.endpoints import meter_model_catalog, meter_model_full_graph, meter_model_apply_changeset, meter_model_edit_dynamic_ports, meter_model_create_dynamic_ports, meter_model_test
from api.v2.marketing import register_demo_user