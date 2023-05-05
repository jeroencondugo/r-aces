import { Injectable } from '@angular/core';
import { of } from 'rxjs';
import { switchMapTo, map, mergeMap, catchError, withLatestFrom } from 'rxjs/operators';
import { select, Store } from '@ngrx/store';
import { createEffect, Actions, ofType } from '@ngrx/effects';

import { LoaderService } from '@core/services/loader.service';
import { NavigationActions, NotificationsActions } from '@core/actions';
import { State } from '@core/reducers';
import { ClusterManagementService } from '../servlces/cluster-management.service';
import { ClusterActions } from '../actions';
import { ClusterManagementSelectors } from '../selectors';

@Injectable()
export class ClusterManagementEffects {
  loadClusters$ = createEffect(() =>
    this.loader.onceForDomainFromRoute('/app/cluster-mgmt').pipe(map(() => ClusterActions.load())),
  );

  getClusters$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.load),
      switchMapTo(this.clusterService.load().pipe(map((clusters) => ClusterActions.loadSuccess({ clusters })))),
    ),
  );

  createCluster$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.create),
      mergeMap(({ cluster: pendingCluster }) =>
        this.clusterService.create(pendingCluster).pipe(
          map((cluster) => ClusterActions.createSuccess({ cluster })),
          catchError((err) => of(ClusterActions.createFail({ err: err || err?.message }))),
        ),
      ),
    ),
  );

  createClusterSuccess$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.createSuccess),
      map(({ cluster: { name } }) =>
        NotificationsActions.success({ text: `Cluster ${name} created`, title: `Create cluster` }),
      ),
    ),
  );

  createClusterFail$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.createFail),
      map(() => NotificationsActions.error({ text: `Failed to create cluster`, title: `Create cluster` })),
    ),
  );

  updateCluster$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.update),
      withLatestFrom(this.store.pipe(select(ClusterManagementSelectors.clusters.getSelectedId))),
      mergeMap(([{ cluster: { active, name } }, id]) =>
        this.clusterService.update({ active, name, id }).pipe(
          map((cluster) => ClusterActions.updateSuccess({ cluster })),
          catchError((err) => of(ClusterActions.updateFail({ err: err || err?.message }))),
        ),
      ),
    ),
  );

  updateClusterSuccess$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.updateSuccess),
      map(({ cluster: { name } }) =>
        NotificationsActions.success({ text: `Cluster ${name} updated`, title: `Update cluster` }),
      ),
    ),
  );

  updateClusterFail$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.updateFail),
      map(() => NotificationsActions.error({ text: `Failed to update cluster`, title: `Update cluster` })),
    ),
  );

  deleteCluster$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.remove),
      mergeMap(({ cluster: { id } }) =>
        this.clusterService.delete(id).pipe(map((cluster) => ClusterActions.removeSuccess({ cluster }))),
      ),
    ),
  );

  deleteClusterSuccess$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.removeSuccess),
      map(() =>
        NotificationsActions.success({
          text: `Cluster marked for termination`,
          title: `Cluster termination`,
        }),
      ),
    ),
  );

  deleteClusterFail$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.removeFail),
      map(() =>
        NotificationsActions.error({
          text: `Failed to mark cluster for termination`,
          title: `Cluster termination`,
        }),
      ),
    ),
  );

  selectCluster$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.selectCluster),
      map(({ cluster: { id } }) => NavigationActions.go({ path: [`app/cluster-mgmt/clusters/${id}`] })),
    ),
  );

  selectClusterAfterCreate$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.createSuccess),
      map(({ cluster: { id } }) => NavigationActions.go({ path: [`app/cluster-mgmt/clusters/${id}`] })),
    ),
  );

  selectClusterAfterEdit$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.updateSuccess),
      map(({ cluster: { id } }) => NavigationActions.go({ path: [`app/cluster-mgmt/clusters/${id}`] })),
    ),
  );
  banClient$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.banClient),
      mergeMap(({ clients: clientIds, cluster }) =>
        this.clusterService.ban(cluster, clientIds).pipe(
          map((response) => ClusterActions.banClientSuccess(response)),
          catchError((err) => of(ClusterActions.banClientFail({ err }))),
        ),
      ),
    ),
  );

  unbanClient$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.unbanClient),
      mergeMap(({ clients: clientIds, cluster }) =>
        this.clusterService.unban(cluster, clientIds).pipe(
          map((response) => ClusterActions.unbanClientSuccess(response)),
          catchError((err) => of(ClusterActions.unbanClientFail({ err }))),
        ),
      ),
    ),
  );

  afterClientStatusChange$ = createEffect(() =>
    this.actions.pipe(
      ofType(ClusterActions.unbanClientSuccess, ClusterActions.banClientSuccess),
      map((_) => ClusterActions.load()),
    ),
  );

  constructor(
    private loader: LoaderService,
    private actions: Actions,
    private clusterService: ClusterManagementService,
    private store: Store<State>,
  ) {}
}
