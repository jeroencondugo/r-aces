from datetime import datetime

from marshmallow import Schema, fields

from cdg_service.schemes.base_schema import base_schema
from cdg_service.schemes.graph import graph_node_port_input_schema, graph_node_port_output_schema
from cdg_service.schemes.meter_config import MeterConfigField
from cdglib.models_client import Meter


class MeasureSchema(Schema):
    id = fields.Integer(description='Measure ID', required=True)
    name = fields.String(description='Measure name', required=True)
    category = fields.String(description='Measure category', required=True)
    unit = fields.String(description='Measure unit', required=True)
    categories = fields.List(fields.String(), required=True)
    dimensionality = fields.String(description='Measure dimensionality', required=False)


class NodeSchema(Schema):
    node_id = fields.Integer(attribute=id, description='Node ID', required=True)
    basetree_id = fields.Function(lambda obj: obj.hierarchy.id, description='Basetree ID', required=True)


class MeterTypeSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    selectable = fields.Function(lambda obj: True if obj.name != "Autovirtual" else False)


def base_meter_schema(model_cls: 'Meter', ip_model_cls: 'GraphNodePortInput', op_model_cls: 'GraphNodePortOutput'):
    GraphNodePortInputSchema = graph_node_port_input_schema(ip_model_cls)
    GraphNodePortOutputSchema = graph_node_port_output_schema(op_model_cls)

    class BaseMeterSchema(base_schema(model_cls, exclude_fields=['disposed', 'changed_at', 'changed', 'source_config',
                                                             'report_settings', 'write_config'])):

        measure = fields.Nested(MeasureSchema, description='', required=True)
        changed_at = fields.DateTime(description='UTC timestamp', default=datetime.utcnow())
        input_ports = fields.Nested(GraphNodePortInputSchema, description='', many=True, required=True)
        output_ports = fields.Nested(GraphNodePortOutputSchema, description='', many=True, required=True)
        nodes = fields.Method('serialize_nodes')


        def serialize_nodes(self, obj):
            """ Serialize nodes """
            nodes = [{"node_id": s.id, "basetree_id": s.hierarchy.id} for s in obj.sites]
            return nodes

    return BaseMeterSchema


def meter_read_schema(model_cls: 'Meter'):
    class MeterReadSchema(base_schema(model_cls, exclude_fields=[
        'disposed', 'changed_at', 'changed', 'source_config', 'report_settings', 'write_config', 'input_ports',
        'output_ports', 'configs', 'sparkline', 'organisation', 'alarms', 'alarm_traps', 'subscribers', 'sites'])):
        source_config_id = fields.Integer(attribute='source_config_id', dump_only=True)
        nodes = fields.Method('serialize_nodes')

        def serialize_nodes(self, obj):
            """ Serialize nodes """
            # nd_schema = NodeSchema()
            # [{ "node_id": s.id, "basetree_id": s.hierarchy.id} for s in meter.sites]
            nodes = [{"node_id": s.id, "basetree_id": s.hierarchy.id} for s in obj.sites]
            return nodes

    return MeterReadSchema


def meter_schema(model_cls: 'Meter', ip_model_cls: 'GraphNodePortInput', op_model_cls: 'GraphNodePortOutput'):
    BaseMeterSchema = base_meter_schema(model_cls, ip_model_cls, op_model_cls)

    class MeterSchema(BaseMeterSchema):
        class Meta(BaseMeterSchema.Meta):
            exclude = ['disposed', 'changed_at', 'changed', 'source_config', 'report_settings', 'write_config',
                       'input_ports', 'output_ports', 'configs', 'sparkline', 'organisation', 'alarms',
                       'alarm_traps', 'subscribers', 'sites']

        source_config_id = fields.Integer(attribute='source_config_id', dump_only=True)
        message_tree = fields.Dict(dump_only=True)
        message_summary = fields.String(attribute='message_summary', many=True, dump_only=True)

    return MeterSchema


def create_meter_changeset_schema(model_cls: 'Meter', ip_model_cls: 'GraphNodePortInput', op_model_cls: 'GraphNodePortOutput'):
    BaseMeterSchema = base_meter_schema(model_cls, ip_model_cls, op_model_cls)

    class CreateMeterChangesetSchema(BaseMeterSchema):
        configs = fields.List(MeterConfigField)

    return CreateMeterChangesetSchema


def meter_changeset_schema(model_cls: 'Meter', ip_model_cls: 'GraphNodePortInput', op_model_cls: 'GraphNodePortOutput'):
    BaseMeterSchema = base_meter_schema(model_cls, ip_model_cls, op_model_cls)

    class MeterChangesetSchema(BaseMeterSchema):
        class Meta(BaseMeterSchema.Meta):
            exclude = ['disposed', 'changed_at', 'changed', 'source_config', 'report_settings', 'write_config',
                       'input_ports', 'output_ports', 'sparkline', 'organisation', 'alarms', 'alarm_traps',
                       'subscribers', 'sites']

        configs = fields.List(MeterConfigField, description='', many=True, required=True)
        source_config_id = fields.Integer(attribute='source_config_id', dump_only=True)

    return MeterChangesetSchema


def update_meter_schema(model_cls: 'Meter'):
    class UpdateMeterSchema(base_schema(model_cls, exclude_fields=['changes', 'measure'])):
        measure_id = fields.Integer(attribute='measure_id')

    return UpdateMeterSchema
