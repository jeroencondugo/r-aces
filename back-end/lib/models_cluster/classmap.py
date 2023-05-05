from cdglib.models_domain import ClassMapBase


class ClassMap(ClassMapBase):

    @property
    def CostModel(self) -> "CostModel":
        from cdglib.models_cluster.cost_model import CostModel
        return CostModel

    @property
    def Constant(self) -> "Constant":
        from cdglib.models_cluster.constants import Constant
        return Constant

    @property
    def Meter(self) -> "Meter":
        from cdglib.models_cluster.meter import Meter
        return Meter

    @property
    def node_meter_table(self):
        from cdglib.models_cluster.basetrees.node import node_meter_table
        return node_meter_table

    @property
    def Organisation(self) -> "Organisation":
        from cdglib.models_cluster.organisation import Organisation
        return Organisation

    @property
    def OrganisationSetting(self) -> "OrganisationSetting":
        from cdglib.models_cluster.organisation_settings import OrganisationSetting
        return OrganisationSetting

    @property
    def Node(self) -> "Node":
        from cdglib.models_cluster.basetrees.node import Node
        return Node

    @property
    def NodeLevel(self) -> "NodeLevel":
        from cdglib.models_cluster.basetrees.node_level import NodeLevel
        return NodeLevel

    @property
    def Basetree(self) -> "Basetree":
        from cdglib.models_cluster.basetrees.node_hierarchy import Basetree
        return Basetree

    @property
    def CommodityType(self) -> "CommodityType":
        from cdglib.models_cluster.commodity_type import CommodityType
        return CommodityType

    @property
    def GraphModel(self) -> "GraphModel":
        from cdglib.models_cluster.graph_model.graph_model import GraphModel
        return GraphModel

    @property
    def Product(self) -> "Product":
        from cdglib.models_cluster.basetrees.product import Product
        return Product

    @property
    def ProductionLine(self) -> "ProductionLine":
        from cdglib.models_cluster.basetrees.production_line import ProductionLine
        return ProductionLine

    @property
    def GraphNode(self) -> "GraphNode":
        from cdglib.models_cluster.graph_model.graph_node import GraphNode
        return GraphNode

    @property
    def GraphNodePortInput(self) -> "GraphNodePortInput":
        from cdglib.models_cluster.graph_model.graph_node_port import GraphNodePortInput
        return GraphNodePortInput

    @property
    def GraphNodePortOutput(self) -> "GraphNodePortOutput":
        from cdglib.models_cluster.graph_model.graph_node_port import GraphNodePortOutput
        return GraphNodePortOutput

    @property
    def GraphNodeDistributor(self) -> "GraphNodeDistributor":
        from cdglib.models_cluster.graph_model.graph_node import GraphNodeDistributor
        return GraphNodeDistributor

    @property
    def GraphNodeConverter(self) -> "GraphNodeConverter":
        from cdglib.models_cluster.graph_model.graph_node import GraphNodeConverter
        return GraphNodeConverter

    @property
    def GraphNodeSink(self) -> "GraphNodeSink":
        from cdglib.models_cluster.graph_model.graph_node import GraphNodeSink
        return GraphNodeSink

    @property
    def GraphNodeSource(self) -> "GraphNodeSource":
        from cdglib.models_cluster.graph_model.graph_node import GraphNodeSource
        return GraphNodeSource

    @property
    def GraphModelExport(self) -> "GraphModelExport":
        from cdglib.models_cluster.graph_model.graph_model_export import GraphModelExport
        return GraphModelExport

    @property
    def ass_graphnode_site(self) -> "ass_graphnode_site":
        from cdglib.models_cluster.graph_model.graph_node import ass_graphnode_site
        return ass_graphnode_site

    @property
    def Ratio(self) -> "Ratio":
        from cdglib.models_cluster.ratio import Ratio
        return Ratio

    @property
    def GraphNodeReport(self) -> "GraphNodeReport":
        from cdglib.models_cluster.graph_model.graph_node_report import GraphNodeReport
        return GraphNodeReport

    # Historian related
    @property
    def Historian(self) -> "Historian":
        from cdglib.models_cluster.historians import Historian
        return Historian

    @property
    def DefaultHistorian(self) -> "DefaultHistorian":
        from cdglib.models_cluster.historians import DefaultHistorian
        return DefaultHistorian

    @property
    def InfluxHistorian(self) -> "InfluxHistorian":
        from cdglib.models_cluster.historians import InfluxHistorian
        return InfluxHistorian

    @property
    def SQLAHistorian(self) -> "SQLAHistorian":
        from cdglib.models_cluster.historians import SQLAHistorian
        return SQLAHistorian

    # MeterConfig related
    @property
    def MeterConfig(self) -> "MeterConfig":
        from cdglib.models_cluster.meter_configs.meter_config_base import MeterConfig
        return MeterConfig

    @property
    def MeterConfigAccumulate(self) -> "MeterConfigAccumulate":
        from cdglib.models_cluster.meter_configs.meter_config_accumulate import MeterConfigAccumulate
        return MeterConfigAccumulate

    @property
    def MeterConfigAdd(self) -> "MeterConfigAdd":
        from cdglib.models_cluster.meter_configs.meter_config_add import MeterConfigAdd
        return MeterConfigAdd

    def MeterConfigCatalog(self) ->"MeterConfigCatalog":
        from cdglib.models_cluster.meter_configs.meter_config_catalog import MeterC

    @property
    def MeterConfigBinaryOperator(self) -> "MeterConfigBinaryOperator":
        from cdglib.models_cluster.meter_configs.meter_config_binary_operator import MeterConfigBinaryOperator
        return MeterConfigBinaryOperator

    @property
    def MeterConfigConstant(self) -> "MeterConfigConstant":
        from cdglib.models_cluster.meter_configs.meter_config_constant import MeterConfigConstant
        return MeterConfigConstant


    @property
    def MeterConfigDelta(self) -> "MeterConfigDelta":
        from cdglib.models_cluster.meter_configs.meter_config_delta import MeterConfigDelta
        return MeterConfigDelta

    @property
    def MeterConfigEnergyToPower(self) -> "MeterConfigEnergyToPower":
        from cdglib.models_cluster.meter_configs.meter_config_energy_to_power import MeterConfigEnergyToPower
        return MeterConfigEnergyToPower

    @property
    def MeterConfigHistorian(self) -> "MeterConfigHistorian":
        from cdglib.models_cluster.meter_configs.meter_config_historian import MeterConfigHistorian
        return MeterConfigHistorian

    @property
    def MeterConfigLimit(self) -> "MeterConfigLimit":
        from cdglib.models_cluster.meter_configs.meter_config_limit import MeterConfigLimit
        return MeterConfigLimit

    @property
    def MeterConfigMeter(self) -> "MeterConfigMeter":
        from cdglib.models_cluster.meter_configs.meter_config_meter import MeterConfigMeter
        return MeterConfigMeter

    @property
    def MeterConfigPowerToEnergy(self) -> "MeterConfigPowerToEnergy":
        from cdglib.models_cluster.meter_configs.meter_config_power_to_energy import MeterConfigPowerToEnergy
        return MeterConfigPowerToEnergy

    @property
    def MeterConfigPumpPower(self) -> "MeterConfigPumpPower":
        from cdglib.models_cluster.meter_configs.meter_config_pump_power import MeterConfigPumpPower
        return MeterConfigPumpPower

    @property
    def MeterConfigRepeatData(self) -> "MeterConfigRepeatData":
        from cdglib.models_cluster.meter_configs.meter_config_repeat_data import MeterConfigRepeatData
        return MeterConfigRepeatData

    @property
    def MeterConfigScalarOperator(self) -> "MeterConfigScalarOperator":
        from cdglib.models_cluster.meter_configs.meter_config_scalar_operator import MeterConfigScalarOperator
        return MeterConfigScalarOperator

    @property
    def MeterConfigSelect(self) -> "MeterConfigSelect":
        from cdglib.models_cluster.meter_configs.meter_config_select import MeterConfigSelect
        return MeterConfigSelect

    @property
    def MeterConfigTankConsumption(self) -> "MeterConfigTankConsumption":
        from cdglib.models_cluster.meter_configs.meter_config_tank_consumption import MeterConfigTankConsumption
        return MeterConfigTankConsumption

    @property
    def MeterConfigTest(self) -> "MeterConfigTest":
        from cdglib.models_cluster.meter_configs.meter_config_test import MeterConfigTest
        return MeterConfigTest

    @property
    def MeterConfigThermalPower(self) -> "MeterConfigThermalPower":
        from cdglib.models_cluster.meter_configs.meter_config_thermal_power import MeterConfigThermalPower
        return MeterConfigThermalPower

    @property
    def MeterModelWarning(self) -> "MeterModelWarning":
        from cdglib.models_cluster.meter_models.meter_model_warning import MeterModelWarning
        return MeterModelWarning


    @property
    def MeterModelEdge(self) -> "MeterModelEdge":
        from cdglib.models_cluster.meter_models.meter_model_edge import MeterModelEdge
        return MeterModelEdge



    @property
    def MeterModelGraphLink(self) -> "MeterModelGraphLink":
        from cdglib.models_cluster.meter_models.meter_model_graph_link import MeterModelGraphLink
        return MeterModelGraphLink



    @property
    def MeterModelNode(self) -> "MeterModelNode":
        from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_node import MeterModelNode
        return MeterModelNode



    @property
    def MeterModelMeter(self) -> "MeterModelMeter":
        from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_meter import MeterModelMeter
        return MeterModelMeter



    @property
    def MeterModelConstant(self) -> "MeterModelConstant":
        from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_constant import MeterModelConstant
        return MeterModelConstant

    @property
    def MeterModelHistorian(self) -> "MeterModelHistorian":
        from cdglib.models_cluster.meter_models.meter_models_nodes.meter_model_historian import MeterModelHistorian
        return MeterModelHistorian

    @property
    def TimeseriesMeterData(self) ->"TimeseriesMeterData":
        from cdglib.models_cluster.data_manager.timeseries_meter_data import TimeseriesMeterData
        return TimeseriesMeterData

    @property
    def TimeseriesData(self) -> "TimeseriesData":
        from cdglib.models_cluster.data_manager.timeseries_data import TimeseriesData
        return TimeseriesData