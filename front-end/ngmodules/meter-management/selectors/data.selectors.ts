import { createFeatureSelector, createSelector } from '@ngrx/store';
import { groupBy } from '@shared/utils/collection.utils';
import { MeterManagementState } from '../reducers';

const getState = createFeatureSelector<MeterManagementState>('meter-management');
const getDataState = createSelector(getState, ({ data }) => data);

const getConfigTypesIds = createSelector(getDataState, ({ configTypeIds }) => configTypeIds);
export const getConfigTypesEntities = createSelector(getDataState, ({ configTypes }) => configTypes);
export const getConfigTypesArray = createSelector(getConfigTypesIds, getConfigTypesEntities, (ids, entities) =>
  ids.map((id) => entities[id]),
);
export const getConfigTypesByCategory = createSelector(getConfigTypesEntities, (entities) => {
  const categoriesDict = groupBy(entities, 'category') || {};
  return Object.keys(categoriesDict).map((key) => ({ name: key, configs: categoriesDict[key] }));
});
