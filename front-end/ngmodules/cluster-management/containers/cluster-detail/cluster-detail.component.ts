import { Component, OnDestroy, ChangeDetectionStrategy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { filter, mapTo, takeUntil, map, take } from 'rxjs/operators';
import { Store, select } from '@ngrx/store';

import { State } from '@core/reducers';
import { OverlayGlobalService } from '@core/services/overlay-global.service';
import { DialogService } from '@core/services/dialog.service';
import { notNull } from '@shared/utils/common.utils';
import { NavigationActions } from '@core/actions';
import { Id } from '@shared/models/id.model';
import { ClusterManagementSelectors } from '../../selectors';
import { Cluster, ClusterClient } from '../../model/cluster.model';
import { ClusterActions } from '../../actions';
import { BanDialogComponent } from '../../components/ban-dialog/ban-dialog.component';
import * as fromRoot from '@core/reducers';

@Component({
  selector: 'cdg-cluster-detail',
  templateUrl: './cluster-detail.component.html',
  styleUrls: ['./cluster-detail.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClusterDetailComponent implements OnDestroy {
  private unsubscribe$ = new Subject();

  readonly selectedCluster$ = this.store.pipe(select(ClusterManagementSelectors.clusters.selectedDenormalized));
  readonly isActive$ = this.selectedCluster$.pipe(map(({ active }) => active));
  readonly hasClients$ = this.selectedCluster$.pipe(map(({ clients }) => clients.length > 0));
  readonly clusterClients$ = this.selectedCluster$.pipe(map(({ clients }) => clients));
  readonly canEdit$ = this.store.pipe(select(fromRoot.getHasAccessToPermission('CLUSTER', 'UPDATE')));
  readonly canDelete$ = this.store.pipe(select(fromRoot.getHasAccessToPermission('CLUSTER', 'DELETE')));

  onEdit({ id }: Cluster) {
    this.store.dispatch(NavigationActions.go({ path: [`app/cluster-mgmt/clusters/edit/${id}`] }));
  }

  onTerminate(cluster: Cluster) {
    this.dialogService
      .danger('Terminate cluster', `Are you sure you want to terminate cluster ${cluster.name}?`, 'TERMINATE', 'CANCEL')
      .pipe(
        filter((confirmed) => confirmed === true),
        mapTo(ClusterActions.remove({ cluster })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }

  onToggleBanned(client: ClusterClient, cluster: Cluster) {
    if (client.banned) {
      this.store.dispatch(ClusterActions.unbanClient({ clients: [client.id], cluster: cluster.id }));
    } else {
      const { save$ } = this.overlayService.create<{ reason: string; clientId: Id }>(
        { clientId: client.id, reason: null },
        BanDialogComponent,
        null,
      );
      save$
        .pipe(
          take(1),
          map(({ reason, clientId }) => ClusterActions.banClient({ reason, clients: [clientId], cluster: cluster.id })),
        )
        .subscribe(this.store);
    }
  }

  ngOnDestroy() {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }

  constructor(
    private store: Store<State>,
    private dialogService: DialogService,
    private route: ActivatedRoute,
    private overlayService: OverlayGlobalService,
  ) {
    this.route.paramMap
      .pipe(
        map((params) => params.get('id')),
        notNull(),
        map((id) => ClusterActions.selected({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }
}
