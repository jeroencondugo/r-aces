import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { map, takeUntil, withLatestFrom } from 'rxjs/operators';
import { select, Store } from '@ngrx/store';

import { State } from '@core/reducers/permissions';
import { notNull } from '@shared/utils/common.utils';
import { Id } from '@shared/models/id.model';
import { ClusterManagementSelectors } from '../../selectors';
import { TerminationActions } from '../../actions';

@Component({
  selector: 'cdg-termination-edit',
  templateUrl: './terminations-edit.container.html',
  styleUrls: ['./terminations-edit.container.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TerminationsEditContainer implements OnInit, OnDestroy {
  private readonly unsubscribe$ = new Subject();
  private readonly selectedCluster$ = new BehaviorSubject<Id>(null);
  readonly showSpinner$ = this.store.pipe(select(ClusterManagementSelectors.terminations.saving));

  readonly clusters$ = this.store.pipe(
    select(ClusterManagementSelectors.clusters.availableClusters),
    map((clusters) => clusters.map(({ id, name }) => ({ id, name }))),
  );

  readonly clients$: Observable<{ id: Id; name: string }[]> = this.selectedCluster$.pipe(
    takeUntil(this.unsubscribe$),
    withLatestFrom(this.store.pipe(select(ClusterManagementSelectors.terminations.clientsPerCluster))),
    map(([clusterId, clientsPerCluster]) => clientsPerCluster[clusterId] ?? []),
  );

  form: FormGroup;

  onClusterSelected(clusterId: Id) {
    this.selectedCluster$.next(clusterId);
  }

  onReset() {
    this.form.reset({});
  }

  onSave({ value }: FormGroup) {
    this.store.dispatch(TerminationActions.create({ termination: { ...value } }));
  }

  ngOnInit() {
    this.form = this.fb.group({
      clients: [[], [Validators.required]],
      cluster: ['', [Validators.required]],
      expiresAt: ['', []],
    });
  }

  ngOnDestroy() {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
    this.selectedCluster$.complete();
  }

  constructor(private route: ActivatedRoute, private store: Store<State>, private fb: FormBuilder) {
    this.route.paramMap
      .pipe(
        map((params) => params.get('id')),
        notNull(),
        map((id) => TerminationActions.selected({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }
}
