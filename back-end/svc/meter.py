import json
from datetime import datetime
from io import StringIO
from typing import List, Optional, Union

import pandas as pd
from pydantic import Field
from pydantic.dataclasses import dataclass
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import selectinload

from cdg_service.errors import NotFound, InvalidParameter
from cdg_service.schemes.meter_config import serializer_registry_client, serializer_registry_cluster
from cdg_service.service.common.base_service import Service, ServiceReturnType
from cdg_service.service.common.meter_type import MeterType
from cdg_service.service.historian import HistorianService
from cdg_service.service.meter_config import meter_config_registry_client, meter_config_registry_cluster
from cdg_service.service.meter_model.meter_model_service import MeterModelService
from cdg_service.service.meters.meter_data_service import MeterDataService
from cdglib import get_all_subclasses
from cdglib.df_manipulator import DataframeManipulator as DFM
from cdglib.measure import MeasureRegister, Measure
from cdglib.measurement_aggregator import MeasurementAggregator
from cdglib.meter_type import MeterType
from cdglib.models_domain.meter_configs.meter_config_dataclasses import MeterConfigHistorian
from cdglib.models_domain.meter_data_classes import MetersExport
from cdglib.period import Period
from cdglib.resolution import Resolution


@dataclass
class MeterNodeChange:
    basetree_id: int
    meter_id: int
    node_id: Optional[int] = None
    original_id: Optional[int] = None


@dataclass
class MeterNodeChangesPayload:
    changes: List[MeterNodeChange] = Field(default_factory=list)


@dataclass
class MeterNodeChangesResponse:
    success: List[MeterNodeChange] = Field(default_factory=list)
    failed: List[MeterNodeChange] = Field(default_factory=list)


class MeterService(Service):

    def create(self, **kwargs):
        """ Create a new meter
            Example payload:
            {   "name":"testje",
                "measureId":1001,
                "changes":[
                    {"basetreeId":"1","nodeId":null,"meterId":null},
                    {"basetreeId":"2","nodeId":null,"meterId":null},
                    {"basetreeId":"3","nodeId":null,"meterId":null},
                    {"basetreeId":"4","nodeId":null,"meterId":null}]}
        """
        # TODO: use it with CreateParam later
        session = self.session
        # required_args = set(["name", "type", "measure", "changes"])
        # if not required_args.issubsetset((kwargs.keys())):

        try:
            measure = int(kwargs['measure_id'])
        except (TypeError, ValueError, KeyError):
            measure = None
        registered_measure = MeasureRegister.get_id(1002)
        if measure:
            if isinstance(measure, int):
                registered_measure = MeasureRegister.get_id(measure)
            else:
                registered_measure = MeasureRegister.get(measure)

        if not registered_measure:
            raise Exception(f'{self.class_name}: measure \'{measure}\' is unknown')

        organisation = session.query(self._classmap.Organisation).first()
        if not organisation:
            raise Exception('{}: organisation not found'.format(self.class_name))
        # Cretae meter
        meter = self._classmap.Meter(kwargs['name'], '', registered_measure)
        meter.organisation_id = organisation.id

        # Set import_uuid if present
        if 'import_uuid' in kwargs and kwargs['import_uuid'] is not None:
            meter.import_uuid = kwargs['import_uuid']
        # organisation.register_meter(meter)
        self.apply_create_changes(kwargs['changes'], meter)
        #   self.apply_node_changes(kwargs['changes'])

        session.add(meter)
        session.flush()

        return meter

    def read(self, meter_ids: List[int] = [], meter_type: Optional[str] = None, commodity_type_id: Optional[int] = None,
             measure: Optional[str] = None, disposed: bool = False, configs: bool = False, config_ids: bool = False,
             nodes: bool = False, input_ports: bool = False, output_ports: bool = False, return_type: ServiceReturnType = ServiceReturnType.OBJECTS, import_uuid: Optional[str] = None):
        if isinstance(meter_ids, int):
            meter_ids = [meter_ids]

        Meter = self._classmap.Meter
        Node = self._classmap.Node
        node_meter_table = self._classmap.node_meter_table

        mtrs = self.session.query(Meter)
        # filter by meter_ids
        if meter_ids:
            mtrs = mtrs.filter(Meter.id.in_(meter_ids))
        # filter by measure
        if measure and measure in ['usage', 'energy', 'power', 'cost']:
            filtered_measures = MeasureRegister.get_measures_from_category(measure)
            filtered_measure_ids = [m.id for m in filtered_measures]
            mtrs = mtrs.filter(Meter.measure_id.in_(filtered_measure_ids))
        # Filter by meter type
        if meter_type:
            if meter_type == "1" or meter_type.lower() == 'auto':
                mtrs = mtrs.filter_by(meter_type=1)
            elif meter_type == "2" or meter_type.lower() == 'manual':
                mtrs = mtrs.filter_by(meter_type=2)
        # Filter by associated commodity type id
        if commodity_type_id:
            mtrs = mtrs.join(node_meter_table).filter(node_meter_table.c.node_id == commodity_type_id)
        # Filter by disposed flag
        if disposed is not None:
            mtrs = mtrs.filter(Meter.disposed == disposed)
        # filter on import_uuid property
        if import_uuid:
            mtrs = mtrs.filter(Meter.import_uuid == import_uuid)
        # optionally load configs
        if configs:
            mtrs = mtrs.options(
                selectinload(Meter.configs).selectin_polymorphic(self._classmap.meter_config_sub_classes))
        # optionally load nodes
        if nodes:
            mtrs = mtrs.options(
                selectinload(Meter.sites).selectin_polymorphic(self._classmap.node_subclasses).selectinload(
                    Node.parent).selectinload(Node.parent), selectinload(Meter.sites).selectinload(Node.hierarchy))
        # optionally load input ports from graph model
        if input_ports:
            mtrs = mtrs.options(selectinload(Meter.input_ports))
        # optionally load output ports from graph model
        if output_ports:
            mtrs = mtrs.options(selectinload(Meter.output_ports))
        # optionally load config ids # TODO: implemnt config_ids switch
        if return_type == ServiceReturnType.OBJECTS:
            return mtrs.all()
        elif return_type == ServiceReturnType.QUERY:
            return mtrs
        else:
            # TODO: Return observable of query object
            return mtrs

    def update(self, meter_id, config_id, data):
        # TODO add param(s) later
        session = self.session
        schema = self._classmap.UpdateMeterSchema()
        organisation = session.query(self._classmap.Organisation).first()
        if not organisation:
            raise Exception('{}: organisation not found'.format(self.class_name))

        meter = session.query(self._classmap.Meter).filter_by(id=meter_id).first()
        res, error = schema.load(data, session=session, instance=meter, partial=True)
        if 'meter_type' in data:
            if data['meter_type'] is not None:
                meter.meter_type = MeterType.get_by_name(data['meter_type'])['id']
        if not meter:
            raise Exception('{}: meter \'{}\' is unknown'.format(self.class_name, meter_id))

        config = session.query(self._classmap.MeterConfig).filter_by(id=config_id).first()
        #       if not config:
        #          raise Exception('{}: meter config \'{}\' is unknown'.format(self.class_name, config_id))
        if config:
            meter.register_config(config)
        # organisation.register_meter(meter)
        # meter = res.data
        if 'changes' in data:
            self.node_changes(changes=data)
        # session.add(meter)
        session.add(organisation)

        return meter

    def delete(self, meter_id):
        session = self.session

        meter = session.query(self._classmap.Meter).filter_by(id=meter_id).first()
        if not meter:
            raise Exception('{}: meter \'{}\' is unknown'.format(self.class_name, meter_id))

        mtr_mdl_service = MeterModelService(self.session)
        mtr_mdl_service.delete_meter_models(meter.id)

        session.delete(meter)
        session.flush()
        return meter

    def search(self, param):
        raise NotImplementedError

    def set_source_config(self, meter_id, config_id):
        session = self.session
        meter = session.query(self._classmap.Meter).get(meter_id)
        if not meter:
            raise Exception('{}: meter \'{}\' is unknown'.format(self.class_name, meter_id))

        if config_id:
            for c in meter.configs:
                if c.id == config_id:
                    meter.set_source_config(c)
        else:
            meter.set_source_config(None)

        session.commit()
        return meter

    def test(self, id: int, period: Union[Period, str] = Period.YEAR) -> None:
        """ Test the meter by requesting the data for last period and storing the results """
        # Fetch meter
        session = self.session
        meters = self.read(meter_ids=[id], configs=True)
        meter = None
        if len(meters) > 0:
            meter = meters[0]
        if meter:
            # Get data for Period
            stop = datetime.utcnow()
            start = stop - period.delta
            message_tree = None
            meter_data_service = MeterDataService(self.session)
            df = meter_data_service.read_raw(meter.id, start, stop)
            # df = meter.get_data(start, stop)
            rows_read = len(df.index) if df is not None else 0
            message_summary = [
                f"Read {rows_read} rows for meter {meter.name} for interval [{start.isoformat()}, {stop.isoformat()})"]
            message_tree = meter.get_message_tree()
            # pprint(message_tree)
            # print("="*80)
            if message_tree:
                meter.message_tree = message_tree
            else:
                meter.message_tree = {}
            # Fetch message_tree and store in meter
            if message_tree:
                meter.message_tree = message_tree
            # Create message tree summary and store in meter
            if message_tree:
                if 'messages' in message_tree:
                    message_summary.append(
                        f"Meter {meter.name}, id: {meter.id} has {len(message_tree['messages'])} messages!")
                if 'input_configs' in message_tree:
                    configs = message_tree['input_configs']
                    # print(f"{configs}, Type: {type(configs)}")
                    config_messages = self._summary_input_configs(message_tree['input_configs'])
                    message_summary = message_summary + config_messages
            meter.message_summary = message_summary
            self.session.commit()
            return meter
        else:
            return None

    def get_heatmap_meter_data(self, excess: List[int], demand: List[int], period: Period, resolution: Resolution,
                               start_date: datetime, measure: Measure, timezone="Europe/Brussels"):
        """ Fetch the data for heatmap excess, demand and overlap tool


        """
        all_meters_ids = excess + demand
        meters = self.read(meter_ids=all_meters_ids, configs=True)
        # Filter all meters based on measure dimensionality
        filtered_meters = [m for m in meters if m.measure.dimensionality == measure.dimensionality]
        # Split meters between excess and demand
        excess_meters = [m for m in filtered_meters if m.id in excess]
        demand_meters = [m for m in filtered_meters if m.id in demand]
        # Setup end_date based on start_date and period
        end_date = period.end_date_per_period(start_date)
        # Loop over the excess meters and fetch data for period, interpolate to resolution, scale to unit and aggregate
        excess_df = pd.DataFrame()
        if excess_meters:
            excess_df = self._aggregate_meters(excess_meters, start_date, end_date, measure, resolution, timezone)
            # excess_df.index = excess_df.index.tz_localize(tz="UTC").tz_convert(timezone)
        demand_df = pd.DataFrame()
        if demand_meters:
            demand_df = self._aggregate_meters(demand_meters, start_date, end_date, measure, resolution, timezone)
            # demand_df.index = demand_df.index.tz_localize(tz="UTC").tz_convert(timezone)
        overlap_min_df = pd.DataFrame()
        overlap_minus_df = pd.DataFrame()
        if not excess_df.empty and not demand_df.empty:
            if excess_df.__len__() > 0:
                overlap_min_df = DFM.binary_operation(excess_df, demand_df, "min")
                overlap_minus_df = DFM.binary_operation(excess_df, demand_df, "minus")
                if not overlap_minus_df.empty:
                    overlap_minus_df = overlap_minus_df.tz_convert(timezone)
                if not overlap_min_df.empty:
                    overlap_min_df = overlap_min_df.tz_convert(timezone)
        else:
            overlap_min_df = None
            overlap_minus_df = None
        if not demand_df.empty:
            demand_df = demand_df.tz_convert(timezone)
        else:
            demand_df = None
        if excess_df.empty:
            excess_df = None
        else:
            excess_df.tz_convert(timezone)
        return excess_df, demand_df, overlap_min_df, overlap_minus_df

    def _aggregate_meters(self, meters, start: datetime, end: datetime, measure: Measure, resolution: Resolution,
                          timezone="Europe/Brussels"):
        """ Aggregate meters for resolution"""
        aggr = MeasurementAggregator(target_unit=measure.unit, target_interval=resolution.offset)
        for mtr in meters:
            raw_df = MeterDataService(self.session).read(mtr.id, start, end)
            aggr.add_dataframe(raw_df, unit=mtr.measure.unit)
        result_df = aggr.aggregate()
        return result_df

    def get_meter_data(self, id: int, period: Period, resolution: Resolution, start_date: datetime):
        """ Test the meter by requesting the data and storing the results """
        begin = start_date if start_date else datetime(1970, 2, 1)
        end = datetime(2200, 1, 1)
        meters = self.read(meter_ids=[id], configs=True)
        if not meters:
            meters = []

        for meter in meters:
            df = MeterDataService(self.session).read(meter.id, begin, end)
            print(df.head(10))
            # df.insert(loc=0, column='timestamp', value=df.index.values.astype(np.int64) // 10 **6)
            # df = df.dropna()
            # df = df.astype(int)

        data = {}
        data['id'] = id
        data['name'] = meter.name
        data['measure_name'] = meter.measure.name
        data['measure_unit'] = meter.measure.unit
        data['data'] = df.values.tolist()
        return data

    def _summary_input_configs(self, configs):
        """ Process all input configs and summarize the messages and process sub input configs """
        message_summary = []
        for input_config in configs:
            # print(f"{input_config}, Type: {type(input_config)}")
            if 'messages' in input_config and input_config['messages']:
                message_summary.append(
                    f"Input config {input_config['name']} has {len(input_config['messages'])} issues")
        return message_summary

    def apply_changeset(self, meter_id, changeset):
        session = self.session

        MeterConfig = self._classmap.MeterConfig
        meter_configs = {}
        meters_configs = session.query(MeterConfig).filter(MeterConfig.meter_id == meter_id).all()

        if 'configs' in changeset:
            configs_data = changeset['configs']
            if self._domain.startswith("cl_"):
                serializer_registry = serializer_registry_cluster
                meter_config_registry = meter_config_registry_cluster
            else:
                serializer_registry = serializer_registry_client
                meter_config_registry = meter_config_registry_client

            def determine_meter_type(configs_data, m_configs):
                create = configs_data.get('create', set([]))
                remove = configs_data.get('remove', set([]))
                existing_configs = create + [vars(config) for config in m_configs if config.id not in remove]
                changeset_number = len(existing_configs)
                t = MeterType.MANUAL
                if changeset_number > 1:
                    return 3
                elif changeset_number == 1:

                    type = existing_configs[0].get('type') if 'type' in existing_configs[0] else existing_configs[0][
                        'discriminator']
                    if type in ['MeterConfigHistorian']:
                        return 2
                    else:
                        return 3
                else:
                    return 3

            if 'remove' in configs_data:
                ids = configs_data['remove']
                # affected = result['removed']

                if len(ids):
                    for meter_config in session.query(MeterConfig).filter(MeterConfig.id.in_(ids)).all():
                        # disconnect from the meter
                        meter_config.meter_id = None
                        meter_config.meter = None

                        session.delete(meter_config)
                        # affected.append(meter)

            # First, we load all JSON data for MeterConfigs that shall be created in common list which will be shared by
            # both 'create' and 'update' changeset
            create_data = configs_data.get('create', [])

            # Second, we will find all MeterConfig that exists in the DB
            existing_configs = {}
            if 'update' in configs_data:
                for config_data in configs_data['update']:
                    if 'id' in config_data:
                        id = config_data['id']
                        if isinstance(id, int) or (isinstance(id, str) and id.isdigit()):
                            # integer ID: we expect this item to exist in the DB, so we will load this item from the DB
                            # and update fields passed in changeset, thus add JSON config data to proper dictionary
                            existing_configs[int(id)] = config_data
                        else:
                            # string ID: we expect this item to be created. since already parsed, add it to list of those
                            # to be created
                            create_data.append(config_data)

            # Third, get all existing MeterConfigs from the DB
            meter_config_ids = list(existing_configs.keys())
            if meter_config_ids:
                found_ids = set()
                for meter_config in session.query(MeterConfig).filter(MeterConfig.id.in_(meter_config_ids)).all():
                    meter_configs[meter_config.id] = meter_config
                    found_ids.add(meter_config.id)

                # in case some of the given IDs are integers, but not found in the DB, try to schedule them for creation
                missing_ids = set(meter_config_ids).difference(found_ids)
                for missing_id in missing_ids:
                    create_data.append(existing_configs[missing_id])

            # Fourth, create MeterConfig objects out of given JSON data, attach to meter and add them to meter_config dictionary
            for config_data in create_data:
                config_type = config_data['type']

                serializer = serializer_registry[config_type]()
                meter_config = meter_config_registry[config_type]

                # TODO: next 2 check are to cover UI bug for presentation. 17.05.2019.
                if 'regular_data' in config_data and config_data['regular_data'] is None:
                    config_data['regular_data'] = False

                if 'synchronized_data' in config_data and config_data['synchronized_data'] is None:
                    config_data['synchronized_data'] = False

                res = serializer.load(config_data, session=session, instance=meter_config, partial=True)
                if res.errors:
                    raise InvalidParameter(f"Error(s) occurred while parsing {config_type}")
                meter_config.meter_id = meter_id
                meter_configs[config_data['id']] = meter_config

                session.add(meter_config)
                # res = serializer.load(config_data, session=session, instance=meter_config, partial=True).data
                # res.meter_id = meter_id
                # meter_configs[config_data['id']] = res
                #
                # session.add(res)

            # Fifth, update meter, iterate through changeset, connect/disconnect ports and add MeterConfigs to session
            meter = session.query(self._classmap.Meter).get(meter_id)  # (int(changeset['id']))
            serializer = self._classmap.CreateMeterChangesetSchema(dump_only=('id', 'configs',))
            res = serializer.load(changeset, session=session, instance=meter, partial=True)
            registered_configs = session.query(MeterConfig).filter_by(meter_id=meter.id)
            registered_configs_dict = {config.id: config for config in registered_configs}
            meter_configs = {**meter_configs, **registered_configs_dict}
            if 'source_config_id' in changeset:
                config_id = changeset['source_config_id']
                if config_id:
                    if isinstance(config_id, int) or (isinstance(config_id, str) and config_id.isdigit()):
                        meter.source_config_id = int(config_id)
                    else:
                        # config_id = int(config_id.rsplit('_', 1)[1])
                        if config_id not in meter_configs:
                            raise NotFound('Source config {} is not known'.format(config_id))
                    meter.source_config = meter_configs[config_id]
                else:
                    meter.source_config_id = None
                    meter.set_source_config(None)

            def connect_input_port(meter_config_id, input_ports, meter_configs):
                if isinstance(meter_config_id, int) or (
                        isinstance(meter_config_id, str) and meter_config_id.isdigit()):
                    meter_config_id = int(meter_config_id)

                if not meter_config_id in meter_configs:
                    raise NotFound('No MeterConfig with ID {} found'.format(meter_config_id))

                meter_config = meter_configs[meter_config_id]

                for input_port in input_ports:
                    if 'output_port_id' in input_port:
                        port_id = input_port['id']
                        if isinstance(port_id, str) and port_id.isdigit():
                            port_id = int(port_id)
                        elif isinstance(port_id, str):
                            try:
                                port_name = port_id.rsplit('_', 1)[1]
                                # TODO: sometimes we get port name and sometimes port ID from the UI
                                if port_name.isdigit():
                                    port_id = int(port_name)
                                else:
                                    port_id = meter_config.input_port_names().index(port_name)
                            except ValueError:
                                # TODO: log or propagate?
                                print("Value error port id")
                                port_id = None
                        elif not isinstance(port_id, int):
                            port_id = None

                        if port_id is not None:
                            ports = meter_config.port_list
                            ports_count = len(ports)
                            if port_id >= ports_count:
                                raise NotFound(
                                    'Port ID {} is out of range ({}) for MeterConfig {}'.format(port_id, ports_count,
                                                                                                meter_config_id))

                            output_port_id = input_port['output_port_id']
                            # if output_port_id:
                            if isinstance(output_port_id, int) or (
                                    isinstance(output_port_id, str) and output_port_id.isdigit()):
                                output_port_id = int(output_port_id)
                            elif output_port_id:
                                output_port_id = output_port_id.rsplit('_', 1)[0]

                            if output_port_id in meter_configs:
                                output_meter_config = meter_configs[output_port_id]
                            else:
                                output_meter_config = session.query(MeterConfig).filter(
                                    MeterConfig.id == output_port_id).first()  # .get(output_port_id)
                                # if not output_meter_config:
                                #     raise NotFound('Output Port ID {} not found for MeterConfig {}'.format(output_port_id, meter_config_id))

                                meter_configs[output_port_id] = output_meter_config

                            # TODO: clean up a bit, why do we need setattr.
                            port_name = meter_config.port_name_list[port_id]
                            # ports[port_id] = output_meter_config
                            setattr(meter_config, "port_%s" % port_name, output_meter_config)
                session.add(meter_config)

            if 'create' in configs_data:
                for config_data in configs_data['create']:
                    if 'input_ports' in config_data:
                        connect_input_port(config_data['id'], config_data['input_ports'], meter_configs)

            if 'update' in configs_data:
                for config_data in configs_data['update']:
                    if 'input_ports' in config_data:
                        connect_input_port(config_data['id'], config_data['input_ports'], meter_configs)

                    # TODO: next 2 check are to cover UI bug for presentation. 17.05.2019.
                    if 'regular_data' in config_data and config_data['regular_data'] is None:
                        config_data['regular_data'] = False

                    if 'synchronized_data' in config_data and config_data['synchronized_data'] is None:
                        config_data['synchronized_data'] = False

                    meter_config = meter_configs[config_data['id']]
                    serializer = serializer_registry[meter_config.discriminator]()
                    res = serializer.load(config_data, session=session, instance=meter_config, partial=True)
                    session.add(meter_config)

        type = determine_meter_type(configs_data, meters_configs)
        setattr(meter, 'meter_type', type)
        session.add(meter)
        session.commit()
        # res = serializer.dump(meter)
        return meter

    def types(self):
        return MeterType.get_meter_types()

    def measures(self):
        return MeasureRegister.measures

    def attached_nodes(self):
        session = self.session

        meters = session.query(self._classmap.Meter).all()
        o = []
        for mtr in meters:
            o.append({"id": mtr.id, "tag": "osi/pi-tag", "nodes": [node.id for node in mtr.sites], "name": mtr.name})

        return o

    def apply_node_changes(self, changes: MeterNodeChangesPayload):
        session = self.session
        Meter = self._classmap.Meter
        Node = self._classmap.Node
        successful_changes = []
        failed_changes = []
        for chg in changes.changes:
            print(chg)
            if not chg.meter_id:
                failed_changes.append(chg)
                continue
            print(f"Meter id: {chg.meter_id}")
            mtr = session.query(Meter).get(chg.meter_id)
            if mtr: print(f"Meter name: {mtr.name}")
            if mtr is None:
                failed_changes.append(chg)
                continue
                # TODO: Check if nodes are part of the basetree with basetree_id
            original_node = session.query(Node).get(chg.original_id) if chg.original_id else None
            new_node = session.query(Node).get(chg.node_id) if chg.node_id else None
            print(f"Original node: {original_node} - New node: {new_node}")
            if not original_node:  # Meter is not connected to a node in this basetree.
                if new_node:  # Meter was not connected but is now attached to node
                    # print "Connecting new node"
                    new_node.connect_meter(mtr)
            else:  # Meter is connected to node original_id in this basetree.
                if not new_node:  # node is not connected to a new node in this basetree: meter is no longer connected to this basetree.
                    # print "Disconnecting original node"
                    original_node.disconnect_meter(mtr)
                else:  # node is now connected to node_id in this basetree.
                    # print "Disconnecting original node and connecting new node"
                    original_node.disconnect_meter(mtr)
                    new_node.connect_meter(mtr)
            successful_changes.append(chg)
        return successful_changes, failed_changes

    def apply_create_changes(self, changes, meter):
        session = self.session
        for chg in changes:
            if "meter_id" not in chg or "basetree_id" not in chg or "node_id" not in chg:
                print("Change malformed! change not processed!")
                continue
            if chg["node_id"] is None and "original_id" not in chg:
                print("Change malformed! change not processed!")
                continue
            node_id = chg['node_id']
            new_node = session.query(self._classmap.Node).get(node_id) if node_id is not None else None
            if new_node:
                new_node.connect_meter(meter)
            else:
                raise ValueError('Node with {} does not exist in database'.format(node_id))

    def export_meters(self, meter_ids: List[int]) -> MetersExport:
        """ export meters with ids in meter_ids to a list of dataclasses."""
        meters = self.read(meter_ids=meter_ids, configs=True)
        for m in meters[:1]:
            for c in m.configs[:1]:
                from pprint import pprint
                pprint(c.to_dict())
                mc = MeterConfigHistorian(**c.to_dict())
        # export historians and nested meters as well
        all_meters = set(meters)
        all_nested_meters = set()
        for m in meters:
            nested_meters = self._find_nested_meters(m)
            all_nested_meters = all_nested_meters.union(nested_meters)
        all_meters = all_meters.union(all_nested_meters)
        historians = set()
        for m in meters:
            m_historians = self._find_historians(m)
            historians = historians.union(m_historians)

        medc_dict = {
            "meters": [m.to_dict() for m in all_meters],
            "historians": [h.to_dict() for h in historians]
        }
        medc = MetersExport(**medc_dict)
        return medc

    def import_meters(self, json_string: str):
        """ Import meters from a json string """
        # Convert json string to objects
        data = json.load(StringIO(json_string))
        medc = MetersExport(**data)
        # Fetch organisation
        org = self.session.query(self._classmap.Organisation).first()
        # Setup historians if they do not exist
        known_historians = self.session.query(self._classmap.Historian).all()
        known_historian_identifiers = {h.identifier: h for h in known_historians}
        historians_per_id = {}
        for hist in medc.historians:
            if hist.identifier in known_historian_identifiers:
                historians_per_id[hist.id] = known_historian_identifiers[hist.identifier]
            else:
                # Create historian
                new_historian = self._classmap.Historian()
                new_historian.organisation_id = org.id
                new_historian.type = hist.type
                new_historian.server = hist.server
                new_historian.port = hist.port
                new_historian.db_name = hist.db_name
                new_historian.username = hist.username
                new_historian.password = hist.password
                new_historian.default_time_column_name = hist.default_time_column_name
                new_historian.default_value_column_name = hist.default_value_column_name
                self.session.add(new_historian)
                self.session.flush()
                historians_per_id[hist.id] = new_historian
        # Create meters and meter_configs
        known_meters = self.session.query(self._classmap.Meter).all()
        known_meters_by_name = {m.name: m for m in known_meters}
        for mtr in medc.meters:
            print("&" * 20, "Importing", mtr.name)
            # Setup new meter object
            new_mtr = self._classmap.Meter()
            new_mtr.organisation_id = org.id
            new_meter_name = mtr.name
            # If meter with this name exist add imported to the name
            if mtr.name in known_meters_by_name:
                new_meter_name = f"{mtr.name} (Imported)"
                # If meter with name including imported exists add counter starting at 2
                if new_meter_name in known_meters_by_name:
                    id = 2
                    while True:
                        new_meter_name_with_counter = f"{new_meter_name} {id}"
                        id += 1
                        if new_meter_name_with_counter not in known_meters_by_name:
                            break
                    new_meter_name = new_meter_name_with_counter
            new_mtr.name = new_meter_name
            new_mtr.measure_id = mtr.measure_id
            new_mtr.changed = mtr.changed
            new_mtr.changed_at = datetime.utcnow()
            new_mtr.meter_type = mtr.meter_type
            new_mtr.verbose = False
            if not mtr.message_tree:
                new_mtr.message_tree = MutableDict()
            else:
                new_mtr.message_tree = mtr.message_tree
            if not mtr.message_summary:
                new_mtr.message_summary = MutableList()
            else:
                new_mtr.message_summary = mtr.message_summary
            new_mtr.disposed = False
            new_mtr.source_config_id = None
            new_mtr.write_config = None
            new_mtr.configs = []
            self.session.add(new_mtr)
            self.session.flush()
            # Setup meter configs
            all_mc_sub_classes = get_all_subclasses(self._classmap.MeterConfig)
            sub_classes_by_name = {mcc.__name__: mcc for mcc in all_mc_sub_classes}
            new_config_by_id = {}
            config_by_id = {cfg.id: cfg for cfg in mtr.configs}
            for cfg in mtr.configs:
                print("$" * 20, "Importing config", cfg.name, " - ", cfg.type)
                # create config
                mc_class = sub_classes_by_name.get(cfg.type)
                if not mc_class:
                    raise TypeError(f"Meter config type {cfg.type} not recognised")
                new_mc = mc_class()
                # Fetch all attributes of new_mc which we need to set which are not internals or callables (methods)
                new_mc_attrs = self._get_mc_attrs(new_mc)
                for attr in new_mc_attrs:
                    if hasattr(cfg, attr):
                        if attr in ("id", "catalog_id", "historian_id", "historian"): continue
                        if attr.startswith("port_"): continue
                        if attr == "regular_data":
                            print(attr, "set to", getattr(cfg, attr))
                        try:

                            setattr(new_mc, attr, getattr(cfg, attr))
                            if attr == "regular_data":
                                print(attr, "has been set to", getattr(new_mc, attr))
                        except AttributeError as e:
                            print(f"Can't set attribute: {attr}, trying _{attr}")
                            # Try with adding a _ before the attr, so interval -> _interval
                            try:
                                new_value = getattr(cfg, attr)
                                setattr(new_mc, f"_{attr}", new_value)
                            except AttributeError as e:
                                print(f"Can't set attribute: _{attr}")
                    if hasattr(new_mc, "schema") and hasattr(cfg, "hist_schema"):
                        setattr(new_mc, "schema", getattr(cfg, "hist_schema"))
                new_mc.meter = new_mtr
                self.session.add(new_mc)
                self.session.flush()
                new_config_by_id[cfg.id] = new_mc

            # now attach meter configs to the ports of other meterconfigs
            for cfg in mtr.configs:
                new_mc = new_config_by_id.get(cfg.id)
                port_attrs = self._get_mc_port_attrs(new_mc)
                print(f"Port attrs: {port_attrs}")
                for pattr in port_attrs:
                    new_mc_attached_to_port = new_config_by_id.get(getattr(cfg, pattr))
                    if new_mc_attached_to_port:
                        print(
                            f"Connecting {new_mc.name}-{pattr} to {new_mc_attached_to_port.id} - {getattr(cfg, pattr)}")
                        setattr(new_mc, pattr, new_mc_attached_to_port.id)
                # Setup historian
                if hasattr(new_mc, "historian_id") and hasattr(cfg, "historian_id"):
                    new_mc.historian = historians_per_id.get(cfg.historian_id)
            # Setup source config on meter
            new_source_mc = new_config_by_id.get(mtr.source_config_id)
            if new_source_mc:
                new_mtr.source_config = new_source_mc

            self.session.commit()

    def _get_mc_attrs(self, meter_config):
        """ Return all attrutes for a meter config to set """
        return [attr for attr in dir(meter_config) if
                not (attr.startswith('__') or attr.startswith('_')) and not callable(getattr(meter_config, attr))]

    def _get_mc_port_attrs(self, meter_config):
        """ Return all attrutes for a meter config to set """
        return [attr for attr in dir(meter_config) if
                attr.startswith('port_') and attr.endswith('_id') and not callable(getattr(meter_config, attr))]

    def _find_historians(self, meter) -> set:
        """ Find all historians referenced in this meter """
        historian_ids = set()
        for c in meter.configs:
            if c.__class__.__name__ == "MeterConfigHistorian":
                historian_ids.add(c.historian_id)
        # load historians
        service = HistorianService(self.session)
        if historian_ids:
            historians = set(service.read(historian_ids=list(historian_ids)))
        else:
            historians = set()
        return historians

    def _find_nested_meters(self, meter) -> set:
        """ Find all historians referenced in this meter """
        source_meter_ids = set()
        for c in meter.configs:
            if c.__class__.__name__ == "MeterConfigMeter":
                source_meter_ids.add(c.source_meter_id)
        # load source_meters
        if source_meter_ids:
            source_meters = set(self.read(meter_ids=list(source_meter_ids), configs=True))
        else:
            source_meters = set()
        nested_meters = set()
        for source_meter in source_meters:
            sm_nested_meters = self._find_nested_meters(source_meter)
            nested_meters = nested_meters.union(sm_nested_meters)
        return source_meters.union(nested_meters)

    # ++++++++++++++++++++++++++++++++ Private methods ++++++++++++++++++++++++++

    def _meter_payload(self, name, measure_id, changes=[]):
        """ Helper function to build a create meter payload """
        return {
            "name": name,
            "measure_id": measure_id,
            "changes": changes
        }

    def _default_changeset_payload(self, meter_id, historian_id, measurement_name, measure_id, unit,
                                   time_col_name="timeStamp", \
                                   val_col_name="value", apply_delta=False, repeat_data=False, regular_data=True,
                                   synchronized_data=False, \
                                   interval="15T", timezone="Europe/Amsterdam"):
        """ Helper function to build a create default historian changeset payload """
        return {
            "id": meter_id,
            "source_config_id": "new_0",
            "configs": {
                "update": [],
                "create": [
                    {
                        "id": "new_0",
                        "type": "MeterConfigHistorian",
                        "catalog_id": "historianSource",
                        "input_ports": [],
                        "output_ports": [
                            {
                                "id": "new_0_0",
                                "name": "",
                                "graph_node_id": "new_0"
                            }
                        ],
                        "name": measurement_name,
                        "measure_id": measure_id,
                        "historian_id": historian_id,
                        "table": measurement_name,
                        "time_column_name": time_col_name,
                        "tz_data": timezone,
                        "value_column_name": val_col_name,
                        "unit": unit,
                        "apply_delta": apply_delta,
                        "repeat_data": repeat_data,
                        "regular_data": regular_data,
                        "synchronized_data": synchronized_data,
                        "interval": interval
                    }
                ],
                "remove": []
            }
        }
