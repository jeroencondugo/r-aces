import { createSelector } from '@ngrx/store';

import { PermissionsSelectors } from '@core/selectors';
import { includesString, pluckId, idIsIn, sameId } from '@shared/utils/common.utils';
import { findPaginatedIds } from '@shared/utils/pagination.utils';
import { DataSelectors } from '@data/selectors';
import { adapter } from '../reducers/cluster-management.reducer';
import { getClustersState } from '../reducers';
import { ClusterClient } from '../model/cluster.model';

const { selectAll, selectEntities } = adapter.getSelectors();

export const clusterEntities = createSelector(getClustersState, selectEntities);
export const getClustersAll = createSelector(getClustersState, selectAll);
export const getLoading = createSelector(getClustersState, (state) => state.loading);
export const getLoaded = createSelector(getClustersState, (state) => state.loaded);
export const getSelectedId = createSelector(getClustersState, (state) => state.selectedCluster);
export const getSelected = createSelector(clusterEntities, getSelectedId, (clusters, id) => clusters[id]);

export const saving = createSelector(getClustersState, (state) => state.saving);
export const selectedDenormalized = createSelector(getSelected, DataSelectors.clients.getEntities, (cluster, clients) =>
  cluster != null
    ? {
        ...cluster,
        clients: <ClusterClient[]>cluster.clients.map((clientId) => ({
          ...clients[clientId],
          banned: cluster.bannedClients.some(sameId(clientId)),
        })),
      }
    : null,
);

export const pageSize = createSelector(getClustersState, (state) => state.pageSize);

const userClusters = createSelector(
  getClustersAll,
  PermissionsSelectors.getCurrentPermissions,
  (clusters, permissions) => {
    const permissionNameList = permissions.map(({ name }) => name);
    return permissionNameList.some((perm) => perm === 'ADMIN_CREATE' || perm === 'CLUSTER_READ')
      ? clusters
      : clusters.slice(0, 2); // TODO: Why only first two clusters???
  },
);

export const searchTerm = createSelector(getClustersState, (state) => state.searchTerm);
export const activePage = createSelector(getClustersState, (state) => state.activePage);

export const availableClusters = createSelector(userClusters, searchTerm, (clusters, term) =>
  clusters.filter((cluster) => includesString(cluster.name, term)),
);
export const visibleClusters = createSelector(activePage, pageSize, availableClusters, (page, _pageSize, entities) => {
  const visibleIds = findPaginatedIds({ page, pageSize: _pageSize, ids: entities.map(pluckId) });
  return entities.filter(({ id }) => idIsIn(visibleIds)({ id }));
});

export const getClusterCount = createSelector(
  userClusters,
  availableClusters,
  activePage,
  ({ length: all }, { length: filtered }) => ({ all, filtered }),
);
