import { createFeatureSelector, createSelector } from '@ngrx/store';

import { ArcSankeyState } from '../reducers';
import { isAfter, isBefore, parseISO } from 'date-fns';
import {
  datetimeSettingsConfig,
  decrementDateConfig,
  incrementDateConfig,
} from '../../energy-insight/reducers/_config';
import { Dict } from '@shared/utils/common.utils';
import { isPeriod, periodComparer, TimePeriod } from '@shared/models/filters';
import { selectItem } from '@shared/utils/selectors.utils';
import { nowISO } from '@shared/utils/date.utils';
import { TimeRange } from '../models/filter-config.model';

export const getState = createFeatureSelector<ArcSankeyState>('arc-sankey');

export const getFilterState = createSelector(getState, ({ filter }) => filter);
export const getConfigsLoaded = createSelector(getFilterState, ({ configsLoaded }) => configsLoaded);

export const getSiteId = createSelector(getFilterState, ({ siteId }) => siteId);
export const getSelectedPeriod = createSelector(getFilterState, ({ selectedPeriod }) => selectedPeriod);
export const getFilterConfigs = createSelector(getFilterState, ({ configEntities }) => configEntities);
const getSelectedSiteConfig = createSelector(getSiteId, getFilterConfigs, selectItem);

export const getIsValidConfig = createSelector(getSelectedSiteConfig, (config) => config != null);

export const getFilterDateRange = createSelector(getSelectedSiteConfig, getSelectedPeriod, (config, selectedPeriod) => {
  const { extends: range } = config ?? { extends: <Dict<TimeRange, TimePeriod>>{} };
  const { startDate, endDate = nowISO() } = range[selectedPeriod] ?? { startDate: null, endDate: null };

  return {
    startDate: startDate != null ? parseISO(startDate) : null,
    endDate: endDate != null ? parseISO(endDate) : null,
  };
});

export const getStartDate = createSelector(getFilterState, ({ startDate }) =>
  startDate != null ? parseISO(startDate) : null,
);

export const getPreviousDisabled = createSelector(
  getFilterDateRange,
  getSelectedPeriod,
  getStartDate,
  ({ startDate }, period, date) => (startDate != null ? isBefore(decrementDateConfig[period](date), startDate) : false),
);

export const getNextDisabled = createSelector(
  getFilterDateRange,
  getSelectedPeriod,
  getStartDate,
  ({ endDate }, period, date) =>
    endDate != null && date != null ? isAfter(incrementDateConfig[period](date), endDate) : false,
);

export const getPeriods = createSelector(getSelectedSiteConfig, (config) => {
  const { extends: range } = config ?? { extends: {} };
  const periods = Object.keys(range).filter(isPeriod).sort(periodComparer);
  return periods;
});

export const getDatetimeOptions = createSelector(getSelectedPeriod, (period) => datetimeSettingsConfig[period]);
export const getMeasureOptions = createSelector(getSelectedSiteConfig, (config) => config?.measureCategories ?? []);
export const getSelectedMeasureOption = createSelector(
  getFilterState,
  ({ selectedMeasureOption }) => selectedMeasureOption,
);
