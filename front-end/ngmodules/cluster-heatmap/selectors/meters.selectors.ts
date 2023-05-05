import { createFeatureSelector, createSelector } from '@ngrx/store';
import { getMeasureId as selectedMeasure } from './filter.selectors';
import { DataSelectors } from '@data/selectors';
import { sameIds } from '@shared/utils/common.utils';
import { ClusterHeatmapState } from '../reducers';
import { stringUtils } from '@shared/utils/string.utils';

const getState = createFeatureSelector<ClusterHeatmapState>('clusterHeatmap');
const getMetersState = createSelector(getState, ({ meters }) => meters);

export const getSelectedExcessMeters = createSelector(getMetersState, ({ excessMeters }) => excessMeters);
export const getSelectedDemandMeters = createSelector(getMetersState, ({ demandMeters }) => demandMeters);

export const getAvailableMeters = createSelector(selectedMeasure, DataSelectors.meters.getAll, (measure, meters) =>
  measure != null
    ? meters
        .filter((meter) => sameIds(measure, meter.measureId))
        .sort((a, b) => stringUtils.insensitiveSorter(a.name, b.name))
    : [],
);

export const getHasAvailableMeters = createSelector(getAvailableMeters, ({ length }) => length > 0);
