import { createSelector } from '@ngrx/store';

import { Dict, idIsIn, notIn, pluckId } from '@shared/utils/common.utils';
import { Id } from '@shared/models/id.model';
import * as fromClients from '@data/selectors/clients.selectors';
import { DataSelectors } from '@data/selectors';
import { findPaginatedIds } from '@shared/utils/pagination.utils';
import { UserClient } from '../../user-management/models/domain-management';
import * as fromTerminations from '../reducers/terminations.reducer';
import { getTerminationsState } from '../reducers';
import { clusterEntities, getClustersAll } from './cluster.selectors';
import { notNull } from '@shared/utils/array.utils';
import { getDenormalizator } from '../utils/utils';

const { selectAll } = fromTerminations.adapter.getSelectors();

export const loading = createSelector(
  getTerminationsState,
  fromClients.getLoading,
  (state, clientsLoading) => state.loading || clientsLoading,
);

export const saving = createSelector(getTerminationsState, (state) => state.saving);
const terminationsAll = createSelector(getTerminationsState, selectAll);
export const selectedId = createSelector(getTerminationsState, (state) => state.selected);

export const getPageSize = createSelector(getTerminationsState, (state) => state.pageSize);
export const activePage = createSelector(getTerminationsState, (state) => state.activePage);

const denormalizeTerminations = createSelector(
  terminationsAll,
  clusterEntities,
  DataSelectors.clients.getEntities,
  (terminations, clusters, clientsEntities) => {
    const denormalizeTermination = getDenormalizator(clientsEntities, clusters);
    return terminations.map(denormalizeTermination);
  },
);

const getSortedTerminations = createSelector(denormalizeTerminations, (terminations) =>
  [...terminations].sort((a, b) => a.status.localeCompare(b.status)),
);

export const visibleTerminations = createSelector(
  activePage,
  getPageSize,
  getSortedTerminations,
  (page, pageSize, terminations) => {
    const visibleIds = findPaginatedIds({ page, pageSize, ids: terminations.map(pluckId) });
    return terminations.filter(idIsIn(visibleIds));
  },
);

export const getCount = createSelector(visibleTerminations, (terminations) => (terminations ?? []).length);

export const selected = createSelector(
  denormalizeTerminations,
  selectedId,
  (terminations, id) => terminations.filter((termination) => termination.id === id)[0],
);

export const clientsPerCluster = createSelector(
  DataSelectors.clients.getEntities,
  getClustersAll,
  terminationsAll,
  (clientEntities, clusters, terminations) => {
    const clientsTerminations = terminations.map(({ clientId }) => clientId);
    return clusters.reduce((agg, { clients, id }) => {
      const nonTerminatedClients = clients.filter(notIn(clientsTerminations));
      return {
        ...agg,
        [id]: nonTerminatedClients.map((clientId) => clientEntities[clientId]).filter(notNull),
      };
    }, <Dict<UserClient[], Id>>{});
  },
);
