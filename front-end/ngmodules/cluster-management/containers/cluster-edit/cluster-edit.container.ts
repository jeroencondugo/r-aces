import { map, shareReplay, startWith, switchMap, take, takeUntil, withLatestFrom } from 'rxjs/operators';
import { of, Subject } from 'rxjs';
import { select, Store } from '@ngrx/store';
import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, Validators } from '@angular/forms';

import { State } from '@core/reducers/permissions';
import { notNull } from '@shared/utils/common.utils';
import { isCreate } from '@shared/models/editor-mode.model';

import { ClusterManagementSelectors } from '../../selectors';
import { ClusterActions } from '../../actions';

@Component({
  selector: 'cdg-cluster-edit',
  templateUrl: './cluster-edit.container.html',
  styleUrls: ['./cluster-edit.container.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClusterEditContainer implements OnDestroy {
  private unsubscribe$ = new Subject();

  readonly isCreate$ = this.route.data.pipe(map(({ mode }) => isCreate(mode)));
  readonly headerTitle$ = this.isCreate$.pipe(map((create) => (create ? 'Create cluster' : 'Edit cluster')));
  readonly showSpinner$ = this.store.pipe(select(ClusterManagementSelectors.clusters.saving));

  private initObject$ = this.isCreate$.pipe(
    switchMap((createMode) =>
      createMode
        ? of({ name: '', active: true })
        : this.store.pipe(select(ClusterManagementSelectors.clusters.getSelected), notNull(), take(1)),
    ),
    shareReplay({ refCount: true, bufferSize: 1 }),
  );

  readonly form$ = this.initObject$.pipe(
    map((initObject) =>
      this.fb.group({
        name: [initObject.name, [Validators.required]],
        active: initObject.active,
      }),
    ),
    shareReplay({ refCount: true, bufferSize: 1 }),
  );

  readonly resetDisabled$ = this.form$.pipe(
    switchMap((form) =>
      form.statusChanges.pipe(
        startWith(form.status),
        map(() => !form.dirty),
      ),
    ),
  );
  readonly saveDisabled$ = this.form$.pipe(
    switchMap((form) =>
      form.statusChanges.pipe(
        startWith(form.status),
        map(() => !form.valid || !form.dirty),
      ),
    ),
  );

  onSave() {
    this.form$
      .pipe(
        withLatestFrom(this.isCreate$),
        take(1),
        map(([{ value: cluster }, createMode]) =>
          createMode ? ClusterActions.create({ cluster }) : ClusterActions.update({ cluster }),
        ),
      )
      .subscribe(this.store);
  }

  onReset() {
    this.form$.pipe(take(1), withLatestFrom(this.initObject$)).subscribe(([form, initObject]) => {
      form.reset(initObject);
    });
  }

  ngOnDestroy() {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }

  constructor(private route: ActivatedRoute, private fb: FormBuilder, private store: Store<State>) {
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
