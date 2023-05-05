import { EntityAdapter, createEntityAdapter, EntityState } from '@ngrx/entity';
import { on, createReducer, Action } from '@ngrx/store';

import { Id } from '@shared/models/id.model';
import { findSelectedPage, findPaginatedIds } from '@shared/utils/pagination.utils';
import { InviteActions } from '../actions/';
import { InviteNormalized } from '../model/invite.model';

export const adapter: EntityAdapter<InviteNormalized> = createEntityAdapter<InviteNormalized>({
  sortComparer: false,
});

export interface InvitesState extends EntityState<InviteNormalized> {
  loading: boolean;
  loaded: boolean;
  selected: Id;
  searchTerm: string;
  activePage: number;
  pageSize: number;
  saving: boolean;
}

const initialState = adapter.getInitialState({
  loaded: false,
  loading: false,
  saving: false,
  selected: null,
  activePage: 0,
  pageSize: 12,
});

const invitesReducer = createReducer(
  initialState,
  on(InviteActions.load, (state) => ({ ...state, loaded: false, loading: true })),
  on(InviteActions.loadSuccess, (state, { invites }) =>
    adapter.upsertMany(invites, { ...state, loaded: true, loading: false }),
  ),
  on(InviteActions.create, InviteActions.remove, (state) => ({ ...state, saving: true })),
  on(InviteActions.createSuccess, (state, { invites }) => {
    const { ids, entities, pageSize } = adapter.upsertMany(invites, state);
    const selectedId = invites[0]?.id;
    const { selectedPage: activePage } = findSelectedPage({ pageSize, selectedId, ids });
    return { ...state, ids, entities, selected: selectedId, activePage, saving: false };
  }),
  on(InviteActions.removeSuccess, (state, { invite }) => {
    const { entities, ids, pageSize, activePage: page } = adapter.removeOne(<string>invite.id, state);
    const paginatedIds = findPaginatedIds({ pageSize, page, ids });
    const activePage = paginatedIds.length > 0 ? page : page - 1;
    return { ...state, entities, activePage, ids, selected: null, saving: false };
  }),
  on(InviteActions.createFail, InviteActions.removeFail, (state) => ({
    ...state,
    saving: false,
  })),
  on(InviteActions.loadFail, (state) => ({ ...state, loading: false })),
  on(InviteActions.select, (state, { id }) => ({ ...state, selected: id })),
  on(InviteActions.changePage, (state, { page: activePage }) => ({ ...state, activePage })),
  on(InviteActions.acceptSuccess, (state, { invite }) => adapter.upsertOne(invite, state)),
  on(InviteActions.declineSuccess, (state, { invite }) => adapter.upsertOne(invite, state)),
);

export function reducer(state: InvitesState, action: Action) {
  return invitesReducer(state, action);
}
