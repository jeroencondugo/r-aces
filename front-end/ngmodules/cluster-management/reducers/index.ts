import * as fromRoot from '@core/reducers';
import * as fromClusters from './cluster-management.reducer';
import * as fromInvites from './invites.reducer';
import * as fromTerminations from './terminations.reducer';
import { createFeatureSelector, createSelector } from '@ngrx/store';

export interface ClusterManagementState {
  clusters: fromClusters.ClusterState;
  invites: fromInvites.InvitesState;
  terminations: fromTerminations.TerminationsState;
}

export interface State extends fromRoot.State {
  'cluster-management': ClusterManagementState;
}

export const reducers = {
  clusters: fromClusters.reducer,
  invites: fromInvites.reducer,
  terminations: fromTerminations.reducer,
};

const getClustersManagementState = createFeatureSelector<ClusterManagementState>('cluster-management');
export const getClustersState = createSelector(getClustersManagementState, (state) => state.clusters);
export const getInvitesState = createSelector(getClustersManagementState, (state) => state.invites);
export const getTerminationsState = createSelector(getClustersManagementState, (state) => state.terminations);
