import { Sorting } from '@shared/models';
import { Dict } from '@shared/utils/common.utils';
import { sortingTransitions } from '@shared/models/collection';
import { Action, createReducer, on } from '@ngrx/store';
import { Id } from '@shared/models/id.model';
import { MeterMgmtActions } from '../actions';
import { DataActions } from '@data/actions';
import { Nullable } from '@shared/types/nullable.type';

export interface State {
  selectedId: Nullable<Id>;
  pageSize: number;
  selectedPage: number;
  searchTerm: string;
  sortEntities: Dict<Sorting>;
  sortKeys: ReadonlyArray<string>;
}

const initialState: State = {
  selectedId: null,
  pageSize: 10,
  selectedPage: 0,
  searchTerm: '',
  sortEntities: {},
  sortKeys: [],
};

const metersListActions = MeterMgmtActions.metersList;

const metersListReducer = createReducer(
  initialState,
  on(
    metersListActions.selectIdSuccess,
    MeterMgmtActions.configEditor.openConfigGraphEditorSuccess,
    MeterMgmtActions.meterEditor.openMeterEditorSuccess,
    (state, { id: selectedId }) => ({ ...state, selectedId }),
  ),
  on(DataActions.meters.updateSuccess, DataActions.meters.addSuccess, (state, { meter: { id: selectedId } }) => ({
    ...state,
    selectedId,
  })),
  on(DataActions.meters.removeSuccess, (state, { id }) => ({
    ...state,
    selectedId: id === state.selectedId ? null : state.selectedId,
  })),
  on(metersListActions.selectPage, (state, { page: selectedPage }) => ({ ...state, selectedPage })),
  on(metersListActions.searchMeters, (state, { searchTerm }) => ({ ...state, searchTerm })),
  on(metersListActions.sortMeters, (state, { column }) => {
    const originalSort: Sorting = state.sortEntities[column] || 'none';
    const newSorting = sortingTransitions[originalSort];
    const sortEntities = { [column]: newSorting };
    const sortKeys = [column];
    return {
      ...state,
      sortEntities,
      sortKeys,
    };
  }),
  on(metersListActions.multiSortMeters, (state, { column }) => {
    const originalSort = state.sortEntities[column] || 'none';
    const newSorting = sortingTransitions[originalSort];
    const sortKeys = [...state.sortKeys.filter((key) => key !== column), column];
    const sortEntities = {
      ...state.sortEntities,
      [column]: newSorting,
    };
    return {
      ...state,
      sortEntities,
      sortKeys,
    };
  }),
);

export function reducer(state: State, action: Action): State {
  return metersListReducer(state, action);
}
