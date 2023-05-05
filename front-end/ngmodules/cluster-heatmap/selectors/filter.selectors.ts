import { createFeatureSelector, createSelector } from '@ngrx/store';
import { ClusterHeatmapState } from '../reducers';
import { toDate } from '@shared/utils/date.utils';
import {
  datetimeSettingsConfig,
  decrementDateConfig,
  incrementDateConfig,
} from '../../energy-insight/reducers/_config';
import { isAfter, isBefore } from 'date-fns';
import { extractAvailablePeriods, extractAvailableResolutions } from '../utils/filter.utils';
import { DataSelectors } from '@data/selectors';

const getState = createFeatureSelector<ClusterHeatmapState>('clusterHeatmap');

const getFilterState = createSelector(getState, ({ filter }) => filter);

export const getStartDateIso = createSelector(getFilterState, ({ startDate }) => startDate);
export const getStartDate = createSelector(getStartDateIso, toDate);
export const getMeasureId = createSelector(getFilterState, ({ measure }) => measure);

export const getMeasure = createSelector(
  getMeasureId,
  DataSelectors.measures.getEntities,
  (id, measures) => measures[id],
);

export const getConfigsPerMeasure = createSelector(getFilterState, ({ configsPerMeasure }) => configsPerMeasure);
export const getConfig = createSelector(
  getMeasureId,
  getConfigsPerMeasure,
  (measure, configsPerMeasure) => configsPerMeasure[measure],
);

export const getAvailablePeriods = createSelector(getConfig, extractAvailablePeriods);
export const getSelectedPeriod = createSelector(getFilterState, ({ period }) => period);
export const getSelectedResolution = createSelector(getFilterState, ({ resolution }) => resolution);
export const getAvailableResolutions = createSelector(getSelectedPeriod, getConfig, extractAvailableResolutions);
export const getDatetimeOptions = createSelector(getSelectedPeriod, (period) => datetimeSettingsConfig[period]);
export const getMinDate = createSelector(getConfig, (config) => toDate(config?.startDate));
export const getMaxDate = createSelector(getConfig, (config) => toDate(config?.endDate));
export const getPreviousDateDisabled = createSelector(
  getMinDate,
  getStartDate,
  getSelectedPeriod,
  (minDate, date, period) => (minDate != null ? isBefore(decrementDateConfig[period](date), minDate) : false),
);
export const getNextDateDisabled = createSelector(
  getMaxDate,
  getStartDate,
  getSelectedPeriod,
  (maxDate, date, period) => (maxDate != null ? isAfter(incrementDateConfig[period](date), maxDate) : false),
);

export const getQueryParams = createSelector(
  getStartDateIso,
  getMeasureId,
  getSelectedPeriod,
  getSelectedResolution,
  (startDate, measure, period, resolution) => ({ startDate, measure, period, resolution }),
);
