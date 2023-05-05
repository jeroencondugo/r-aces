import { createReducer, on, Action } from '@ngrx/store';
import { EntityAdapter, createEntityAdapter, EntityState } from '@ngrx/entity';

import { Id } from '@shared/models/id.model';
import { findPaginatedIds, findSelectedPage } from '@shared/utils/pagination.utils';
import { ClusterActions } from '../actions';
import { ClusterNormalized } from '../model/cluster.model';

export const adapter: EntityAdapter<ClusterNormalized> = createEntityAdapter<ClusterNormalized>({
  sortComparer: false,
});

export interface ClusterState extends EntityState<ClusterNormalized> {
  loading: boolean;
  loaded: boolean;
  saving: boolean;
  selectedCluster: Id;
  searchTerm: string;
  activePage: number;
  pageSize: number;
}

const initialState = adapter.getInitialState({
  loaded: false,
  loading: false,
  saving: false,
  selectedCluster: null,
  searchTerm: '',
  activePage: 0,
  pageSize: 12,
});

const clustersReducer = createReducer(
  initialState,
  on(ClusterActions.load, (state) => ({ ...state, loading: true, loaded: false })),
  on(ClusterActions.loadSuccess, (state, { clusters }) =>
    adapter.setAll(clusters, { ...state, loading: false, loaded: true }),
  ),
  on(ClusterActions.loadFail, () => initialState),
  on(ClusterActions.create, ClusterActions.remove, (state) => ({ ...state, saving: true })),
  on(ClusterActions.createSuccess, (state, { cluster }) => {
    const { ids, entities, pageSize } = adapter.addOne(cluster, state);
    const selectedId = cluster.id;
    const { selectedPage: activePage } = findSelectedPage({ pageSize, selectedId, ids });
    return { ...state, entities, ids, selectedCluster: selectedId, activePage, saving: false };
  }),
  on(ClusterActions.update, (state) => ({ ...state, saving: true })),
  on(ClusterActions.updateSuccess, (state, { cluster }) => {
    const { ids, entities, pageSize } = adapter.upsertOne(cluster, state);
    const selectedId = cluster.id;
    const { selectedPage: activePage } = findSelectedPage({ pageSize, selectedId, ids });
    return { ...state, entities, selectedCluster: selectedId, activePage, saving: false };
  }),
  on(ClusterActions.removeSuccess, (state, { cluster }) => {
    const { ids, pageSize, activePage: page, entities } = adapter.removeOne(<string>cluster, state);
    const paginatedIds = findPaginatedIds({ pageSize, page, ids });
    const activePage = paginatedIds.length > 0 ? page : page === 0 ? page + 1 : page - 1;
    return { ...state, entities, ids, activePage, selectedCluster: null, saving: false };
  }),
  on(ClusterActions.removeFail, ClusterActions.updateFail, (state) => ({ ...state, saving: false })),
  on(ClusterActions.selected, (state, { id }) => ({ ...state, selectedCluster: id })),
  on(ClusterActions.searchClusters, (state, { term: searchTerm }) => ({ ...state, searchTerm })),
  on(ClusterActions.pageChange, (state, { selectedPage: activePage }) => ({ ...state, activePage })),
);

export function reducer(state: ClusterState, action: Action) {
  return clustersReducer(state, action);
}
