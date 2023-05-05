import { Id } from '@shared/models/id.model';

export interface TimeseriesDataPoint {
  value: number | string;
  timestamp: string;
}

export interface TestDataResults {
  warnings: string[];
  data: readonly TimeseriesDataPoint[];
  id: Id;
}
