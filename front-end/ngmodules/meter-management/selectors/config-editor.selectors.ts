import { createFeatureSelector, createSelector } from '@ngrx/store';
import { MeterManagementState } from '../reducers';
import { size } from '@shared/utils/collection.utils';
import { Dict } from '@shared/utils/common.utils';
import { getSelectedId as getSelectedMeterId } from './meters-list.selectors';
import { DataSelectors } from '@data/selectors';
import { createList } from '@shared/utils/selectors.utils';
import { MeterConfigChangeset } from '../models/changeset.model';

const getState = createFeatureSelector<MeterManagementState>('meter-management');
const getConfigEditorState = createSelector(getState, ({ configEditor }) => configEditor);

export const getIsSaving = createSelector(getConfigEditorState, ({ saving }) => saving);
const getGraphNodeEntities = createSelector(getConfigEditorState, ({ configs }) => configs);
const getInputPortEntities = createSelector(getConfigEditorState, ({ inputPorts }) => inputPorts);
const getOutputPortEntities = createSelector(getConfigEditorState, ({ outputPorts }) => outputPorts);

export const getEntities = createSelector(
  getGraphNodeEntities,
  getInputPortEntities,
  getOutputPortEntities,
  (nodes, inputPorts, outputPorts) => ({ nodes, inputPorts, outputPorts }),
);
export const getChangesetEntities = createSelector(getConfigEditorState, ({ changesetEntities }) => changesetEntities);
export const getChangesetIds = createSelector(getConfigEditorState, ({ changesetIds }) => changesetIds);
export const getRedosCount = createSelector(
  getChangesetIds,
  getChangesetEntities,
  (ids, entities) => size(entities) - ids.length,
);
export const getUndosCount = createSelector(getChangesetIds, ({ length }) => length);
export const getUndoEnabled = createSelector(getUndosCount, (count) => count > 0);
export const getRedoEnabled = createSelector(getChangesetIds, getChangesetEntities, (ids, entities) => {
  const redoId = ids.length;
  const redoChange = entities[redoId];
  return redoChange != null;
});

export const getCleanChangesetEntities = createSelector(getChangesetEntities, getChangesetIds, (entities, ids) =>
  (ids || []).reduce(
    (cleanChangesets, changeId) => ({
      ...cleanChangesets,
      [changeId]: entities[changeId],
    }),
    <Dict<MeterConfigChangeset>>{},
  ),
);

const getTestResultsPerMeterId = createSelector(getConfigEditorState, ({ tests }) => tests);
export const getCurrentTestResults = createSelector(
  getTestResultsPerMeterId,
  getSelectedMeterId,
  (testsPerMeterId, meterId) => testsPerMeterId[meterId] ?? [],
);

export const getConnectedPortId = createSelector(getConfigEditorState, ({ connectedPort }) => connectedPort);

export const getNavigationHistoryIds = createSelector(
  getConfigEditorState,
  ({ navigationHistory }) => navigationHistory,
);
export const getNavigationHistory = createSelector(
  getNavigationHistoryIds,
  DataSelectors.meters.getEntities,
  createList,
);
