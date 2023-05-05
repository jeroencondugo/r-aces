import { Id } from '@shared/models/id.model';
import { HeatmapItem } from '@components/heatmap/heatmap.model';
import { TimePeriod, TimeResolution } from '@shared/models/filters';
import { Dict } from '@shared/utils/common.utils';

export type ClusterHeatmapType = 'excess' | 'demand' | 'overlap' | 'difference';

export interface HeatmapChart {
  id: Id;
  type: ClusterHeatmapType;
  title: string;
  subtitle: string;
  data: readonly HeatmapItem[];
  order: number;
}

export interface HeatmapConfig {
  startDate: string;
  endDate: string;
  resolutions: Partial<Dict<readonly TimeResolution[], TimePeriod>>;
  measure: Id;
}

export interface HeatmapPayload {
  excess?: readonly Id[];
  demand?: readonly Id[];
  period: TimePeriod;
  resolution: TimeResolution;
  startDate: string;
  measure: Id;
}
