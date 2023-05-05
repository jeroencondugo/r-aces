import { Id } from '@shared/models/id.model';
import { Node } from '@components/arc-diagram/arc-diagram.model';

export interface GraphNodeNormalized {
  id: Id;
  label: string;
  name: string;
}

export interface GraphNode extends Node {
  input: number;
  output: number;
  inputUnit: string;
  outputUnit: string;
}
