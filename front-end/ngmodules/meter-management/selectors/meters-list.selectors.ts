import { createFeatureSelector, createSelector } from '@ngrx/store';
import { MeterManagementState } from '../reducers';
import { Sorting } from '@shared/models';

const getState = createFeatureSelector<MeterManagementState>('meter-management');
const getMetersListState = createSelector(getState, ({ metersList }) => metersList);

export const getSelectedId = createSelector(getMetersListState, ({ selectedId }) => selectedId);
export const getPageSize = createSelector(getMetersListState, ({ pageSize }) => pageSize);
export const getSelectedPage = createSelector(getMetersListState, ({ selectedPage }) => selectedPage);
export const getSearchTerm = createSelector(getMetersListState, ({ searchTerm }) => searchTerm);

const getSortingKeys = createSelector(getMetersListState, ({ sortKeys }) => sortKeys);

export const getSorting = createSelector(getMetersListState, ({ sortEntities }) => sortEntities);
export const getSortingArray = createSelector(
  getSortingKeys,
  getSorting,
  (keys, entities) =>
    <ReadonlyArray<{ key: string; order: Sorting }>>(
      keys.map((key) => ({ key, order: entities[key] })).filter((c) => c != null && c.order !== 'none')
    ),
);
