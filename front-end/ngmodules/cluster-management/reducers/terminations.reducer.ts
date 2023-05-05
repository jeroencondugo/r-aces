import { EntityAdapter, createEntityAdapter, EntityState } from '@ngrx/entity';
import { createReducer, Action, on } from '@ngrx/store';

import { findSelectedPage, findPaginatedIds } from '@shared/utils/pagination.utils';
import { Id } from '@shared/models/id.model';
import { TerminationActions } from '../actions';
import { TerminationNormalized } from '../model/termination.model';

export const adapter: EntityAdapter<TerminationNormalized> = createEntityAdapter<TerminationNormalized>({
  sortComparer: false,
});

export interface TerminationsState extends EntityState<TerminationNormalized> {
  loading: boolean;
  loaded: boolean;
  selected: Id;
  searchTerm: string;
  activePage: number;
  pageSize: number;
  saving: boolean;
}

const initialState = adapter.getInitialState({
  saving: false,
  loaded: false,
  loading: false,
  selected: null,
  activePage: 0,
  pageSize: 12,
});

const invitesReducer = createReducer(
  initialState,
  on(TerminationActions.load, (state) => ({ ...state, loading: true, loaded: false })),
  on(TerminationActions.loadSuccess, (state, { terminations }) =>
    adapter.upsertMany(terminations, { ...state, loaded: true, loading: false }),
  ),
  on(TerminationActions.loadFail, () => initialState),
  on(TerminationActions.select, (state, { id }) => ({ ...state, selected: id })),
  on(TerminationActions.changePage, (state, { page: activePage }) => ({ ...state, activePage })),
  on(TerminationActions.acceptSuccess, (state, { termination }) => adapter.upsertOne(termination, state)),
  on(TerminationActions.declineSuccess, (state, { termination }) => adapter.upsertOne(termination, state)),
  on(TerminationActions.create, TerminationActions.remove, (state) => ({ ...state, saving: true })),
  on(TerminationActions.createSuccess, (state, { terminations }) => {
    const { ids, entities, pageSize } = adapter.upsertMany(terminations, state);
    const selectedId = terminations[0]?.id;
    const { selectedPage: activePage } = findSelectedPage({ pageSize, selectedId, ids });
    return { ...state, ids, entities, selected: selectedId, activePage, saving: false };
  }),
  on(TerminationActions.removeSuccess, (state, { termination }) => {
    const { entities, ids, pageSize, activePage: page } = adapter.removeOne(<string>termination.id, state);
    const paginatedIds = findPaginatedIds({ pageSize, page, ids });
    const activePage = paginatedIds.length > 0 ? page : page - 1;
    return { ...state, entities, activePage, ids, selected: null, saving: false };
  }),
  on(TerminationActions.createFail, TerminationActions.removeFail, (state) => ({ ...state, saving: false })),
  on(TerminationActions.loadFail, (state) => ({ ...state, loading: false })),
);

export function reducer(state: TerminationsState, action: Action) {
  return invitesReducer(state, action);
}
