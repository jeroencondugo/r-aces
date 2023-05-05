import { HeatmapConfig } from '../models/heatmap.model';
import { isPeriod, periodComparer, TimePeriod, TimeResolution } from '@shared/models/filters';

export function extractAvailablePeriods(config: HeatmapConfig) {
  if (config == null) {
    return <readonly TimePeriod[]>[];
  }
  const periods = Object.keys(config.resolutions)
    .filter(isPeriod)
    .filter((period) => config.resolutions[period]?.length > 0);

  return periods.sort(periodComparer);
}

export function extractAvailableResolutions(period: TimePeriod, config: HeatmapConfig) {
  if (config == null) {
    return <readonly TimeResolution[]>[];
  }
  return config.resolutions[period] ?? [];
}
