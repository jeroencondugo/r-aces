import { createFeatureSelector, createSelector } from '@ngrx/store';
import { MeterManagementState } from '../reducers';
import { DataSelectors } from '@data/selectors';
import { sameIds } from '@shared/utils/common.utils';
import { selectItem } from '@shared/utils/selectors.utils';

const getState = createFeatureSelector<MeterManagementState>('meter-management');
const getConfigEditorNodeEditorState = createSelector(getState, ({ configEditorNodeDialog }) => configEditorNodeDialog);

export const getOutputMode = createSelector(getConfigEditorNodeEditorState, ({ outputMode }) => outputMode);

const getSelectedMeasureId = createSelector(getConfigEditorNodeEditorState, ({ measure }) => measure);
const getSelectedMeasure = createSelector(getSelectedMeasureId, DataSelectors.measures.getEntities, selectItem);
export const getSelectedBaseDimensionality = createSelector(
  getSelectedMeasure,
  (measure) => measure?.baseDimensionality,
);

export const getAvailableConstants = createSelector(
  getSelectedBaseDimensionality,
  DataSelectors.constants.getList,
  (baseDimensionality, constants) => {
    const shouldReturnMock = Math.random() > 0.5;
    return shouldReturnMock
      ? constants
      : constants.filter((constant) => sameIds(constant.baseDimensionality, baseDimensionality));
  },
);

export const getFieldIsConstant = createSelector(
  getConfigEditorNodeEditorState,
  ({ isConstantField }) => isConstantField,
);
