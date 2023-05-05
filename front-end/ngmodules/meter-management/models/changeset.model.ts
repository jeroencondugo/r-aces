import {
  InputPortAddedChangeset,
  InputPortDeletedChangeset,
  InputPortModifiedChangeset,
  NodeAddedChangeset,
  NodeDeletedChangeset,
  NodeModifiedChangeset,
  OutputPortAddedChangeset,
  OutputPortDeletedChangeset,
  OutputPortModifiedChangeset,
} from '../../structure-management/models/graph-changeset';
import { InputPortNormalized, MeterConfig, MeterConfigNormalized, OutputPortNormalized } from './meter-config.model';
import { Dict } from '@shared/utils/common.utils';
import { Id } from '@shared/models/id.model';

export type MeterConfigChangeset = { id: number } & (
  | NodeAddedChangeset<MeterConfig>
  | NodeModifiedChangeset<MeterConfig>
  | NodeDeletedChangeset<MeterConfig>
  | InputPortAddedChangeset<InputPortNormalized>
  | InputPortModifiedChangeset<InputPortNormalized>
  | InputPortDeletedChangeset
  | OutputPortAddedChangeset<OutputPortNormalized>
  | OutputPortModifiedChangeset<OutputPortNormalized>
  | OutputPortDeletedChangeset
);

export interface Changes {
  nodes: Dict<MeterConfigNormalized>;
  inputPorts: Dict<InputPortNormalized>;
  outputPorts: Dict<OutputPortNormalized>;
}

export type ConfigUpdate = Omit<MeterConfigNormalized, 'inputPorts'> & { inputPorts: readonly InputPortNormalized[] };
export interface ChangesDTO {
  id: Id;
  connectedPort: Id;
  configs: { update: readonly ConfigUpdate[]; create: readonly MeterConfig[]; remove: readonly Id[] };
}
