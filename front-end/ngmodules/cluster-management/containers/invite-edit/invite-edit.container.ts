import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { DateAdapter, MAT_DATE_FORMATS } from '@angular/material/core';
import { MAT_DATEPICKER_SCROLL_STRATEGY_FACTORY_PROVIDER } from '@angular/material/datepicker';
import { map, startWith, takeUntil } from 'rxjs/operators';
import { BehaviorSubject, combineLatest, Observable, Subject } from 'rxjs';
import { select, Store } from '@ngrx/store';

import { State } from '@core/reducers/permissions';
import { notNull, sameIds } from '@shared/utils/common.utils';
import { SHORT_ISO_DATE_FORMATS, ShortIsoDateAdapter } from '@shared/utils/short-iso-date-adapter';
import { Id } from '@shared/models/id.model';
import { isCreate } from '@shared/models/editor-mode.model';
import { ClusterManagementSelectors } from '../../selectors';
import { InviteActions } from '../../actions';
import { Nullable } from '@shared/types/nullable.type';
import { UserClient } from '../../../user-management/models/domain-management';
import { DataSelectors } from '@data/selectors';

@Component({
  selector: 'cdg-invite-edit',
  templateUrl: './invite-edit.container.html',
  styleUrls: ['./invite-edit.container.scss'],
  providers: [
    { provide: MAT_DATE_FORMATS, useValue: SHORT_ISO_DATE_FORMATS },
    { provide: DateAdapter, useClass: ShortIsoDateAdapter },
    MAT_DATEPICKER_SCROLL_STRATEGY_FACTORY_PROVIDER,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InviteEditContainer implements OnInit, OnDestroy {
  unsubscribe$ = new Subject();
  readonly isCreate$ = this.route.data.pipe(map(({ mode }) => isCreate(mode)));
  readonly showSpinner$ = this.store.pipe(select(ClusterManagementSelectors.invites.saving));
  private selectedCluster$ = new BehaviorSubject<Nullable<Id>>(null);

  readonly clusters$ = this.store.pipe(
    select(ClusterManagementSelectors.clusters.availableClusters),
    map((clusters) => clusters.map(({ id, name }) => ({ id, name }))),
  );

  clients$: Observable<{ id: Id; name: string }[]>;

  readonly form = this.fb.group({
    clients: [[], []],
    cluster: ['', []],
    expiresAt: ['', []],
  });

  onReset() {
    this.resetForm();
  }

  onSave({ value }: FormGroup) {
    this.store.dispatch(InviteActions.create({ invite: value }));
  }

  onClusterSelected(clusterId: Id) {
    this.selectedCluster$.next(clusterId);
  }

  private resetForm() {
    this.form.reset({});
  }

  ngOnInit() {
    this.resetForm();

    this.clients$ = combineLatest([
      this.selectedCluster$,
      this.store.pipe(select(DataSelectors.clients.getAll)),
      this.store.pipe(select(ClusterManagementSelectors.invites.invitesAll)),
    ]).pipe(
      map(([clusterId, clients, invites]) => {
        const selectedClusterInvites =
          clusterId == null ? [] : invites.filter((invite) => sameIds(clusterId, invite.clusterId));

        const notInvited = ({ id }: UserClient) =>
          !selectedClusterInvites.some(({ clientId }) => sameIds(id, clientId));

        return clusterId == null ? [] : clients.filter(notInvited);
      }),
    );

    const clusterControl = this.form.get('cluster') as FormControl;
    const clientsControl = this.form.get('clients') as FormControl;

    clusterControl.valueChanges
      .pipe(startWith(<Id>clusterControl.value), takeUntil(this.unsubscribe$))
      .subscribe((clusterId) => {
        if (clusterId == null) {
          clientsControl.disable();
        } else {
          clientsControl.enable();
        }
      });
  }

  ngOnDestroy() {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }

  constructor(private route: ActivatedRoute, private store: Store<State>, private fb: FormBuilder) {
    this.route.paramMap
      .pipe(
        map((params) => params.get('id')),
        notNull(),
        map((id) => InviteActions.selected({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }
}
