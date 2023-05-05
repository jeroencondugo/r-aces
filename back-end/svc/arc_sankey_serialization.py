import copy
import json
import os
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

import pandas as pd

from api.classmap import import_class
from cdg_service.service.graph_model import GraphModelService
from cdg_service.service.sankey_serialization_base import SankeySerializationBaseService
from cdglib import MeasureRegister
from cdglib.influx import influxdb_session
from cdglib.influx.df_influxdb import DataframeInfluxdb
from cdglib.measure import MeasureCategory
from cdglib.models_client import CommodityType
from cdglib.models_domain.graph_model.graph_model_anlysis_dataclasses import MeterMetadataID, MeterMetadata, \
    MeterInfluxMapping
from cdglib.models_domain.graph_model.graph_model_link_dataclasses import LinkV2
from cdglib.models_domain.graph_model.graph_model_node_dataclasses import GraphModelNode
from cdglib.models_domain.graph_model.graph_model_node_report_dataclasses import NodeReport


@dataclass
class DataframeValues:
    value: Optional[float] = None
    value_pp: Optional[float] = None
    value_py: Optional[float] = None


class ArcSankeySerializationService(SankeySerializationBaseService):

    def __init__(self, session=None, config=None):
        super().__init__(session=session, config=config)

    def serialize_site(self, domain: str, site_id: int, period: str, start_date: datetime, end_date: datetime,
                       debug: bool = False):
        """ Serialize the graph model on a single site """
        gm_report: NodeReport = NodeReport()
        load_meta = self._fetch_metadata(site_id, domain)
        if not load_meta:
            return gm_report
        df = self._fetch_arc_sankey_time_series_data(domain, period, start_date, end_date)
        gm_report.nodes, node_pairs_by_label, source_nodes_by_label, sink_nodes_by_label = self._build_nodes(df,
                                                                                                             None,
                                                                                                             None,
                                                                                                             gm_report.links,
                                                                                                             domain,
                                                                                                             site_id)
        gm_report.links, link_messages = self._build_links(df, domain, site_id, period, start_date.isoformat(), node_pairs_by_label)
        gm_report.messages.append(link_messages)
        return gm_report

    @abstractmethod
    def serialize_node(self, client_schema: str, site_id: int, node_id: int, period: str, start_date: datetime,
                       end_date: datetime, mc: MeasureCategory = MeasureCategory.USAGE):
        """ Serialize the graph model on a single graph node with detailed time series """
        raise NotImplementedError

    def _create_graph_model_report(self, domain):
        """ Create a graph model report """
        NodeReport_class = import_class(domain, "NodeReport")
        return NodeReport_class()

    def _fetch_metadata(self, site_id: int, domain: str) -> bool:
        """ Fetch the graph model metadata """
        try:
            self._read_meta_model(site_id)
            return True
        except NodeReportNotFound as e:
            self.logger.error(f"{domain}: {site_id} Node report not found in the database")
            return False

    def _fetch_arc_sankey_time_series_data(self, domain: str, period: str, start_date: datetime,
                                           end_date: datetime) -> pd.DataFrame:
        """ Fetch the time series data """
        # Fetch meter data from influxdb
        domain_id = domain.replace('c_', '').replace('cl_', '')
        # Resolution for the sankey is determined by the period (so only 1 timestamp per flow)
        resolution = period.lower()
        bucket_name = f"{self.app_config.CONDUGO_ENV}-r_{domain_id}-{resolution}"
        with influxdb_session() as influx_client:
            df_client = DataframeInfluxdb(influx_config=self.app_config.influx_config, client=influx_client)
            df_val = self._fetch_link_values(df_client, bucket_name, self.gm.id, period, start_date, end_date)

        return df_val

    def _build_links(self, df: pd.DataFrame, client_schema: str = "", site_id: Optional[int] = None,
                     period: str = "", start_date_iso: str = "", node_pairs_by_label: dict=None, debug: bool = False):
        """Add links to the serialization"""
        if not node_pairs_by_label:
            node_pairs_by_label = {}
        node_pairs_by_sink_node_id = {}
        for label, pair in node_pairs_by_label.items():
            node_pairs_by_sink_node_id[pair[0][1].id] = pair[0]


        out_links = []
        messages = []
        for link_dict in self.arc_sankey_links:
            link = LinkV2(**link_dict)
            # exchange link target id if sink node is in a pair for the source node id of the pair
            node_pair = node_pairs_by_sink_node_id.get(link.target)
            if node_pair:
                link.target = node_pair[0].id
            ct: CommodityType = self.ct_per_id[link.commodity_type]
            column_name = f"val_{link.id}"
            mmi = self.meter_meta_id_per_graph_port_id.get(link.id)
            if mmi and mmi.influx_mapping:
                usage, energy = self._get_values_from_df(df=df, mmi=mmi, ct=ct)
            else:
                usage = DataframeValues()
                energy = DataframeValues()
            usage_atv, usage_messages = self._get_amount_trend_value(link.id, ct.usage_measure, usage.value, usage.value_pp,
                                                             usage.value_py)
            link.usage = usage_atv
            messages.append(usage_messages)
            energy_atv = None
            if ct.is_energy:
                energy_atv, energy_messages = self._get_amount_trend_value(link.id, ct.energy_measure, energy.value, energy.value_pp,
                                                             energy.value_py)
            link.energy = energy_atv
            messages.append(energy_messages)
            out_links.append(link)
        return out_links, messages

    def _build_nodes(self, df, df_ratios, df_dists, links: Optional[List[LinkV2]], client_schema: str, site_id: int,
                     node_id: Optional[int] = None, debug: bool = False):
        """ Build the nodes serialization """
        # TODO: Remove mock data
        file_path = '/etc/condugo/source_sink_mocks.json'
        mock_data_exists = os.path.exists(file_path)
        mock_data_index = None
        if mock_data_exists and client_schema == "c_c448edd01cce22080037d66561a935e0":
            with open(file_path, "r") as fp:
                try:
                    mock_data = json.load(fp)
                except Exception as e:
                    mock_data = None
            if mock_data:
                mock_data_index = {node['nodeId']: node for node in mock_data}
        gm_nodes = []
        # Find pairs of nodes between source and sink nodes with the same label
        # Node pairs are nodes which both source and sink links
        # Source nodes which are not paired will only source links
        # Sink nodes which are not paired will only sink links
        # Paired nodes will have the id of the source node
        node_pairs_by_label = {}
        source_nodes_by_label = {node.label: node for node in self.nodes_per_type['GraphNodeSource']}
        sink_nodes_by_label = {node.label: node for node in self.nodes_per_type['GraphNodeSink']}
        for source_label, source_node in source_nodes_by_label.items():
            if source_label in sink_nodes_by_label:
                sink_node = sink_nodes_by_label[source_label]
                if source_label not in node_pairs_by_label:
                    node_pairs_by_label[source_label] = [(source_node, sink_node)]
                else:
                    node_pairs_by_label[source_label].append((source_node, sink_node))
        source_node_labels = list(set(source_nodes_by_label.keys()) - set(node_pairs_by_label.keys()))
        sink_node_labels = list(set(sink_nodes_by_label.keys()) - set(node_pairs_by_label.keys()))
        source_nodes_by_label = {label: source_nodes_by_label[label] for label in source_node_labels}
        sink_nodes_by_label = {label: sink_nodes_by_label[label] for label in sink_node_labels}
        for node_label, pair_list in node_pairs_by_label.items():
            for pair in pair_list:
                arc_node = self._build_node_from_pair(pair)
            if arc_node:
                gm_nodes.append(arc_node)
        # Add only the source nodes
        for node_label, node in source_nodes_by_label.items():
            gm_node = GraphModelNode(node.id, node.name, node.label)
            gm_nodes.append(gm_node)
        # Add only the sink nodes
        for node_label, node in sink_nodes_by_label.items():
            gm_node = GraphModelNode(node.id, node.name, node.label)
            gm_nodes.append(gm_node)
        return gm_nodes, node_pairs_by_label, source_nodes_by_label, sink_nodes_by_label

    def _build_node_from_pair(self, node_pair):
        """ Build node from a pair of source and sink nodes with the same label """
        source_node = node_pair[0]
        gm_node = GraphModelNode(source_node.id, source_node.name, source_node.label)
        return gm_node

    # ================================= Private methods ========================

    def _read_meta_model(self, site_id: Optional[int] = None, node_id: Optional[int] = None, debug=False):
        """ Read the Graph Node Report and build up the object model """
        self.gm = self.session.query(self._classmap.GraphModel).first()
        self.gm_service = GraphModelService(session=self.session)
        # fetch all buildings and rooms for a site for building or room id
        all_basetree_nodes = self.session.query(self._classmap.Node).all()
        all_ct_nodes = self.session.query(self._classmap.CommodityType).all()
        self.ct_per_id = {ct.id: ct for ct in all_ct_nodes}
        # Fetch all graph nodes for a site
        self.nodes = self.gm_service.read(site_id)
        self.node = None
        # if we filter on a node_id, filter the node_id and all nodes with output ports linked to node_id
        if node_id:
            filtered_nodes = []
            for node in self.nodes:
                if node.id == node_id:
                    self.node = node
                    filtered_nodes.append(node)
                for oport in node.output_ports:
                    if oport.input_port and oport.input_port.graph_node == node_id:
                        filtered_nodes.append(node)
            self.nodes = filtered_nodes
        # Split nodes per type
        self.nodes_per_type = {}
        for node in self.nodes:
            if node.discriminator not in self.nodes_per_type:
                self.nodes_per_type[node.discriminator] = [node]
            else:
                self.nodes_per_type[node.discriminator].append(node)

        self.node_ids = [node.id for node in self.nodes]
        gm_report_name = f"Graph model {self.gm.id} report"
        gm_report_db = self.session.query(self._classmap.GraphNodeReport).filter_by(name=gm_report_name).first()
        if not gm_report_db:
            raise NodeReportNotFound("Node report not found in the database")
        self.meter_metadata_id = gm_report_db.meter_metadata
        if debug: print(f"Length meter metadata id: {len(self.meter_metadata_id)}")
        self.node_metadata_per_node_id = gm_report_db.node_metadata_per_node_id
        self.output_port_ids_per_input_port_id = {int(key): val for key, val in
                                                  gm_report_db.output_port_ids_per_input_port_id.items()}
        self.meter_meta_id = []
        # TODO: Switch to short routes, needs structural refactor
        self.distributions_meta_per_node_id = {}  # gm_report_db.short_distributions_per_node_id
        self.short_route_fields = []
        self.arc_sankey_links = gm_report_db.arc_sankey_links
        # for node_id, dists in self.distributions_meta_per_node_id.items():
        #     for dist in dists:
        #         print(f"Number of destinations: {len(dist['destinations'])}")
        #         for dest in dist['destinations']:
        #             print(f"Number of route items: {len(dest['route_v2'])}")
        #             for ri in dest['route_v2']:
        #                 self.short_route_fields.append(ri['route_field'])

        if debug:
            meters_without_mapping = 0
            for mmi in self.meter_metadata_id:
                if mmi['site_id'] == 4 and not mmi['influx_mapping']:
                    meters_without_mapping += 1
        for mmi in self.meter_metadata_id:
            # filter all metadata not related to this site
            if site_id and mmi['site_id'] and mmi['site_id'] != site_id:
                continue
            # filter all metadata not related to this node
            if node_id and mmi['graph_node_id'] and mmi['graph_node_id'] != node_id:
                continue
            mm_id = MeterMetadataID(**mmi)
            if mmi['influx_mapping']:
                mm_id.influx_mapping = MeterInfluxMapping(**mmi['influx_mapping'])
            self.meter_meta_id.append(mm_id)
        if debug:
            print(f"Meters without mapping: {meters_without_mapping}")
        self.meter_meta_id_per_graph_port_id = {}
        for mm in self.meter_meta_id:
            if mm.graph_port_id not in self.meter_meta_id_per_graph_port_id:
                self.meter_meta_id_per_graph_port_id[mm.graph_port_id] = copy.deepcopy(mm)
        if debug:
            print(
                f"self.meter_meta_id with influx_mapping: {len([mmap for mmap in self.meter_meta_id if mmap.influx_mapping and mmap.influx_mapping.field_name is not None])}")
            print(
                f"self.meter_meta_id with influx_mapping: {len([mmap for key, mmap in self.meter_meta_id_per_graph_port_id.items() if mmap.influx_mapping and mmap.influx_mapping.field_name is not None])}")
        # Build up list of meter_metadata with objects
        self.port_per_port_id = {}
        self.port_mmi = []
        self.port_mmi_per_port_id = {}
        self.port_mm = []
        self.port_mm_per_port = {}
        self.port_mm_per_port_id = {}
        mmi_with_influx_map = []
        for node in self.nodes:
            for col in (node.input_ports, node.output_ports):

                for port in col:
                    if port.id not in self.port_per_port_id:
                        self.port_per_port_id[port.id] = port
                    try:
                        mmi = copy.deepcopy(self.meter_meta_id_per_graph_port_id[port.id])
                        if mmi.influx_mapping and mmi.influx_mapping.field_name is not None:
                            mmi_with_influx_map.append(True)
                        # print(f"type MMI {type(mmi)} and type MMI.influx_mapping {type(mmi.influx_mapping)}")
                        if mmi.usage_measure_id:
                            self.port_mmi.append(mmi)
                            if port.id not in self.port_mmi_per_port_id:
                                self.port_mmi_per_port_id[port.id] = copy.deepcopy(mmi)
                    except KeyError:
                        mmi = None
                    if mmi is not None and mmi.usage_measure_id:
                        mm = MeterMetadata(
                            site=port.graph_node.site,
                            graph_model=self.gm,
                            graph_node=node,
                            graph_port=port,
                            meter=port.meter,
                            commodity_type=port.ct,
                            usage_measure=MeasureRegister.get_id(mmi.usage_measure_id),
                            energy_measure=MeasureRegister.get_id(
                                mmi.energy_measure_id) if mmi.energy_measure_id else None,
                            power_measure=MeasureRegister.get_id(
                                mmi.power_measure_id) if mmi.power_measure_id else None,
                            influx_mapping=copy.deepcopy(mmi.influx_mapping)
                        )
                        # mm.influx_mapping = copy.copy(mmi.influx_mapping)
                        self.port_mm.append(mm)
                        if port not in self.port_mm_per_port:
                            self.port_mm_per_port[port] = mm
                            self.port_mm_per_port[port].influx_mapping = copy.copy(mmi.influx_mapping)
                        if port.id not in self.port_mm_per_port_id:
                            self.port_mm_per_port_id[port.id] = mm
                            self.port_mm_per_port_id[port.id].influx_mapping = copy.copy(mmi.influx_mapping)
        if debug:
            print(f"mmi with influx_mapping: {len(mmi_with_influx_map)}")
            print(
                f"self.port_mmi with influx_mapping: {len([mmap for mmap in self.port_mmi if mmap.influx_mapping and mmap.influx_mapping.field_name is not None])}")
            print(
                f"self.port_mmi_per_port_id with influx_mapping: {len([mmap for key, mmap in self.port_mmi_per_port_id.items() if mmap.influx_mapping and mmap.influx_mapping.field_name is not None])}")
            print(
                f"self.port_mm with influx_mapping: {len([mmap for mmap in self.port_mm if mmap.influx_mapping and mmap.influx_mapping.field_name is not None])}")
            print(
                f"self.port_mm_per_port_id with influx_mapping: {len([mmap for key, mmap in self.port_mm_per_port_id.items() if mmap.influx_mapping and mmap.influx_mapping.field_name is not None])}")

        self.output_ports_per_input_port_id = {}
        for key, val in self.output_port_ids_per_input_port_id.items():
            for port_id in val:
                try:
                    port = self.port_per_port_id[port_id]
                except KeyError:
                    continue
                if key not in self.output_ports_per_input_port_id:
                    self.output_ports_per_input_port_id[key] = [port]
                else:
                    self.output_ports_per_input_port_id[key].append(port)
        # print(Counter([mm.influx_mapping is not None for mm in self.port_mm]))
        # self.output_ports_per_input_port_id = {key: [self.port_per_port_id[port_id] for port_id in val] }



    def create(self, sankey_serialization_dict):
        """ Method to create an sankey_serialization object """
        raise NotImplementedError

    def read(self):
        """ Method to read sankey_serialization objects """
        raise NotImplementedError

    def update(self, sankey_serialization_changes):
        """ Method to edit an sankey_serialization object """
        raise NotImplementedError

    def delete(self, sankey_serialization_id):
        """ Method to delete an sankey_serialization object """
        raise NotImplementedError

    def index(self, sankey_serialization_id):
        """ Method to index an sankey_serialization object """
        raise NotImplementedError


class NodeReportNotFound(Exception):
    """ Exception for when there is not node report in the db """
    pass
