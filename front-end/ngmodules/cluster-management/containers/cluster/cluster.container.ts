import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { PageEvent } from '@angular/material/paginator';
import { FormControl } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, map, takeUntil } from 'rxjs/operators';
import { select, Store } from '@ngrx/store';

import * as fromRoot from '@core/reducers';
import { NavigationActions } from '@core/actions';
import { ClusterNormalized } from '../../model/cluster.model';

import { ClusterManagementSelectors } from '../../selectors';
import { ClusterActions } from '../../actions';

@Component({
  selector: 'cdg-cluster-container',
  templateUrl: './cluster.container.html',
  styleUrls: ['./cluster.container.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClusterContainer implements OnInit, OnDestroy {
  unsubscribe$ = new Subject();
  clusters$ = this.store.pipe(select(ClusterManagementSelectors.clusters.visibleClusters));
  clustersCount$ = this.store.pipe(
    select(ClusterManagementSelectors.clusters.getClusterCount),
    map(({ filtered }) => filtered),
  );
  hintLabel$ = this.store.pipe(
    select(ClusterManagementSelectors.clusters.getClusterCount),
    map(({ all, filtered }) =>
      filtered ? (all !== filtered ? `Displaying ${filtered} / ${all} clusters` : null) : 'No clusters found',
    ),
  );
  activePage$ = this.store.pipe(select(ClusterManagementSelectors.clusters.activePage));
  pageSize$ = this.store.pipe(select(ClusterManagementSelectors.clusters.pageSize));
  loading$ = this.store.pipe(select(ClusterManagementSelectors.clusters.getLoading));
  selectedId$ = this.store.pipe(select(ClusterManagementSelectors.clusters.getSelectedId));
  canEdit$ = this.store.pipe(select(fromRoot.getHasAccessToPermission('CLUSTER', 'UPDATE')));

  searchTermControl = new FormControl('');

  onCreateCluster() {
    this.store.dispatch(NavigationActions.go({ path: ['app/cluster-mgmt/clusters/new'] }));
  }

  onPageSelected({ pageIndex }: PageEvent) {
    this.store.dispatch(ClusterActions.pageChange({ selectedPage: pageIndex }));
  }

  onSelected(cluster: ClusterNormalized) {
    this.store.dispatch(ClusterActions.selectCluster({ cluster }));
  }

  onActiveUpdate(cluster: ClusterNormalized) {
    this.store.dispatch(ClusterActions.update({ cluster }));
  }

  ngOnInit() {
    this.searchTermControl.valueChanges
      .pipe(
        takeUntil(this.unsubscribe$),
        debounceTime(200),
        distinctUntilChanged(),
        map((term) => ClusterActions.searchClusters({ term })),
      )
      .subscribe(this.store);
  }

  ngOnDestroy() {
    this.unsubscribe$.next(null);
  }

  constructor(private store: Store<fromRoot.State>) {}
}
