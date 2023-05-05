import { Nullable } from '@shared/types/nullable.type';
import { Id } from '@shared/models/id.model';
import { MeterConfigMeta } from './data.model';
import { Dict } from '@shared/utils/common.utils';

export enum MeterConfigType {
  SourceMeter = 'MeterModelMeter',
  SourceConstant = 'MeterModelConstant',
  Historian = 'MeterModelHistorian',
  ADD = 'MeterModelAdd',
  BinaryOperator = 'MeterModelBinaryOperator',
  ScalarOperator = 'MeterModelScalarOperator',
  Accumulate = 'MeterModelAccumulate',
  Delta = 'MeterModelDelta',
  EnergyToPower = 'MeterModelEnergyToPower',
  PowerToEnergy = 'MeterModelPowerToEnergy',
  VirtualMeter = 'Meter',
  ThermalPower = 'MeterModelThermalPower',
  Repeat = 'MeterModelRepeatData',
  PumpPower = 'MeterModelPumpPower',
  TankConsumption = 'MeterModelTankConsumption',
  Limit = 'MeterModelLimit',
  Select = 'MeterModelSelect',
  Chromatograph = 'MeterModelChromatograph',
  GenericParser = 'MeterModelGenericParser',
  SteamMassToEnergy = 'MeterModelSteamMassToEnergy',
}

type BinaryOperator = 'plus' | 'minus' | 'times' | 'divide' | 'min' | 'max';
type ScalarOperator = Omit<BinaryOperator, 'min' | 'max'> | 'power';

export interface InputPortNormalized {
  id: Id;
  name: string;
  outputNodeId: Id;
  outputPortId: Id;
  graphNodeId: Id;
}

export interface OutputPortNormalized {
  id: Id;
  name: string;
  graphNodeId: Id;
}

export interface ConfigPortUpdate {
  id: Id;
  inputPorts: readonly InputPortNormalized[];
  outputPorts: readonly OutputPortNormalized[];
}

export interface NormalizedConfigsData {
  configs: Dict<MeterConfigNormalized>;
  configIds: readonly Id[];
  inputPorts: Dict<InputPortNormalized>;
  outputPorts: Dict<OutputPortNormalized>;
}

interface BaseMeterConfig {
  id: Id;
  meterId: Id;
  inputPorts: readonly InputPortNormalized[];
  outputPorts: readonly OutputPortNormalized[];
  metadata: MeterConfigMeta;
  measureId: Id;
  type: MeterConfigType;
  name: string;
  importers: readonly any[];
  tzSource: string;
  label: string;
  autoName: string;
  dynamic: boolean;
}

interface MeterConfigHistorian extends BaseMeterConfig {
  type: MeterConfigType.Historian;
  tableName: string;
  applyDelta: boolean;
}

interface MeterConfigAdd extends BaseMeterConfig {
  type: MeterConfigType.ADD;
  amountInputs: number;
}

interface MeterConfigBinaryOperator extends BaseMeterConfig {
  type: MeterConfigType.BinaryOperator;
  operator: BinaryOperator;
}

interface MeterConfigScalarOperator extends BaseMeterConfig {
  type: MeterConfigType.ScalarOperator;
  operator: ScalarOperator;
  scalar: number;
}

interface MeterConfigPowerToEnergy extends BaseMeterConfig {
  type: MeterConfigType.PowerToEnergy;
}

interface MeterConfigThermalPower extends BaseMeterConfig {
  type: MeterConfigType.ThermalPower;
  density: number;
  heatCapacity: number;
  heating: boolean;
  portFlow: Nullable<Id>;
}

interface MeterConfigTankConsumption extends BaseMeterConfig {
  type: MeterConfigType.TankConsumption;
  maxFillLevel: number;
  maxFillLevelPct: number;
  portFlow: Nullable<Id>;
  portLevel: number;
  startFillLevel: number;
}

interface MeterConfigAccumulate extends BaseMeterConfig {
  type: MeterConfigType.Accumulate;
}

interface MeterConfigDelta extends BaseMeterConfig {
  type: MeterConfigType.Delta;
}

interface MeterConfigEnergyToPower extends BaseMeterConfig {
  type: MeterConfigType.EnergyToPower;
}

interface MeterConfigMeter extends BaseMeterConfig {
  type: MeterConfigType.SourceMeter;
  sourceMeterId: Id;
}

interface MeterConfigConstant extends BaseMeterConfig {
  type: MeterConfigType.SourceConstant;
  value: number;
  beginUtc: Nullable<string>;
  endUtc: Nullable<string>;
}

interface MeterConfigRepeatData extends BaseMeterConfig {
  type: MeterConfigType.Repeat;
}

interface MeterConfigPumpPower extends BaseMeterConfig {
  type: MeterConfigType.PumpPower;
  nomPower: number;
}

interface MeterConfigVirtualMeter extends BaseMeterConfig {
  type: MeterConfigType.VirtualMeter;
}

interface MeterConfigLimit extends BaseMeterConfig {
  type: MeterConfigType.Limit;
  upperLimit: Nullable<number>;
  lowerLimit: Nullable<number>;
}

interface MeterConfigSelect extends BaseMeterConfig {
  type: MeterConfigType.Select;
  compareMode: 'gt' | 'lt';
  outputMode: 'diff' | 'inv_diff' | 'current_or_const' | 'previous_or_const' | 'const_or_const';
  constant1: number;
  constant2: number;
}

interface MeterConfigGenericParser extends BaseMeterConfig {
  type: MeterConfigType.GenericParser;
  formula: string;
}

interface MeterConfigChromatograph extends BaseMeterConfig {
  type: MeterConfigType.Chromatograph;
}

interface MeterConfigSteamMassToEnergy extends BaseMeterConfig {
  type: MeterConfigType.SteamMassToEnergy;
  noTemp: boolean;
}

export type MeterConfig =
  | MeterConfigAccumulate
  | MeterConfigAdd
  | MeterConfigBinaryOperator
  | MeterConfigConstant
  | MeterConfigDelta
  | MeterConfigEnergyToPower
  | MeterConfigHistorian
  | MeterConfigLimit
  | MeterConfigMeter
  | MeterConfigPowerToEnergy
  | MeterConfigPumpPower
  | MeterConfigRepeatData
  | MeterConfigScalarOperator
  | MeterConfigSelect
  | MeterConfigTankConsumption
  | MeterConfigThermalPower
  | MeterConfigChromatograph
  | MeterConfigGenericParser
  | MeterConfigVirtualMeter
  | MeterConfigSteamMassToEnergy;
type NormalizedConfig<TConfig extends BaseMeterConfig> = Omit<TConfig, 'metadata' | 'inputPorts' | 'outputPorts'> & {
  catalogId: Id;
  inputPorts: readonly Id[];
  outputPorts: readonly Id[];
};
export type MeterConfigNormalized =
  | NormalizedConfig<MeterConfigAccumulate>
  | NormalizedConfig<MeterConfigAdd>
  | NormalizedConfig<MeterConfigBinaryOperator>
  | NormalizedConfig<MeterConfigConstant>
  | NormalizedConfig<MeterConfigDelta>
  | NormalizedConfig<MeterConfigEnergyToPower>
  | NormalizedConfig<MeterConfigHistorian>
  | NormalizedConfig<MeterConfigSelect>
  | NormalizedConfig<MeterConfigLimit>
  | NormalizedConfig<MeterConfigMeter>
  | NormalizedConfig<MeterConfigPowerToEnergy>
  | NormalizedConfig<MeterConfigPumpPower>
  | NormalizedConfig<MeterConfigRepeatData>
  | NormalizedConfig<MeterConfigScalarOperator>
  | NormalizedConfig<MeterConfigTankConsumption>
  | NormalizedConfig<MeterConfigThermalPower>
  | NormalizedConfig<MeterConfigGenericParser>
  | NormalizedConfig<MeterConfigChromatograph>
  | NormalizedConfig<MeterConfigSteamMassToEnergy>
  | NormalizedConfig<MeterConfigVirtualMeter>;
