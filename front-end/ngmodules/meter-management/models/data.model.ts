import { MeterConfigType } from './meter-config.model';
import { Dict } from '@shared/utils/common.utils';

interface MeterConfigMetaField {
  name: string;
  value: string | number;
}

export interface MeterConfigMetaPort {
  name: string;
  order: number;
}

export interface MeterConfigMeta {
  type: string;
  category: string;
  operation: MeterConfigType;
  label: string;
  fields: ReadonlyArray<MeterConfigMetaField>;
  inputPorts: readonly MeterConfigMetaPort[];
  outputPorts: readonly MeterConfigMetaPort[];
  autoName: string;
  constants: Dict<{ defaultValue: number; dimension: string; unit: string }>;
  dynamic: boolean;
}
