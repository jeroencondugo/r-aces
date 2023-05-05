import { createSelector } from '@ngrx/store';

import { hasId, idIsIn, pluckId, sameId } from '@shared/utils/common.utils';
import { findPaginatedIds } from '@shared/utils/pagination.utils';
import { DataSelectors } from '@data/selectors';
import { clusterEntities } from './cluster.selectors';
import { adapter } from '../reducers/invites.reducer';
import * as fromAuth from '../../auth/reducers';
import { getInvitesState } from '../reducers';
import { getDenormalizator } from '../utils/utils';

const { selectAll, selectEntities } = adapter.getSelectors();

export const inviteEntities = createSelector(getInvitesState, selectEntities);
export const invitesAll = createSelector(getInvitesState, selectAll);
export const loading = createSelector(
  getInvitesState,
  DataSelectors.clients.getLoading,
  (state, clientsLoading) => state.loading || clientsLoading,
);

export const saving = createSelector(getInvitesState, (state) => state.saving);
export const selectedId = createSelector(getInvitesState, (state) => state.selected);

export const pageSize = createSelector(getInvitesState, (state) => state.pageSize);
export const activePage = createSelector(getInvitesState, (state) => state.activePage);

const organisationInvites = createSelector(invitesAll, fromAuth.getSelectedDomainId, (entities, id) =>
  entities.filter(({ clientId, clusterId }) => sameId(clientId)(id) || sameId(clusterId)(id)),
);

const denormalizedInvites = createSelector(
  organisationInvites,
  clusterEntities,
  DataSelectors.clients.getEntities,
  (invites, clusters, clients) => {
    const denormalizeInvite = getDenormalizator(clients, clusters);
    return invites.map(denormalizeInvite);
  },
);

const sorterInvites = createSelector(denormalizedInvites, (invites) => {
  const sortedSent = invites.sort((a, b) => a.status.localeCompare(b.status));
  return [...sortedSent];
});

export const visibleInvites = createSelector(activePage, pageSize, sorterInvites, (page, _pageSize, entities) => {
  const visibleIds = findPaginatedIds({ page, pageSize: _pageSize, ids: entities.map(pluckId) });
  return entities.filter(idIsIn(visibleIds));
});

export const getCount = createSelector(visibleInvites, (invites) => invites.length);

export const selected = createSelector(denormalizedInvites, selectedId, (invites, id) => invites.find(hasId(id)));

