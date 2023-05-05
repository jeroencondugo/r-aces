import { MeasureOption, TimePeriod } from '@shared/models/filters';
import { Id } from '@shared/models/id.model';

export interface TimeRange {
  endDate: string | null;
  startDate: string | null;
}

export interface FilterConfigResponse {
  extends: {
    D?: TimeRange;
    W?: TimeRange;
    M?: TimeRange;
    Q?: TimeRange;
    Y?: TimeRange;
    All?: TimeRange;
  };
  periods: readonly TimePeriod[];
  measureCategories: readonly MeasureOption[];
}

export type FilterConfig = FilterConfigResponse & { id: Id };
