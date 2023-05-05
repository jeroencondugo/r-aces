import { combineLatest, Observable, Subject } from 'rxjs';
import { filter, map, shareReplay, startWith, switchMap, take, takeUntil, withLatestFrom } from 'rxjs/operators';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { select, Store } from '@ngrx/store';
import * as fromMeterManagement from '../../reducers';
import { Dict, diffObject, isEmpty, notNull } from '@shared/utils/common.utils';
import { DataSelectors } from '@data/selectors';
import { MetersListSelectors } from '../../selectors';
import { Id } from '@shared/models/id.model';
import { commonAnimations } from '@shared/animations';
import { MeterMgmtActions } from '../../actions';
import { DataActions } from '@data/actions';
import { BasetreeConnectionsViewModel } from '@shared/models/meters';
import { generateBasetreeConnections, getConnectionPerBasetree } from '@shared/utils/meter.utils';

@Component({
  selector: 'cdg-meter-edit-detail',
  changeDetection: ChangeDetectionStrategy.OnPush,
  styleUrls: ['./meter-edit.component.scss'],
  templateUrl: './meter-edit.component.html',
  animations: [commonAnimations.fadeAnimation],
})
export class MeterEditComponent implements OnInit, OnDestroy {
  private unsubscribe$ = new Subject();

  measures$ = this._store.pipe(select(DataSelectors.measures.getAll));
  meterName$ = this._store.pipe(
    select(fromMeterManagement.getSelectedMeter),
    map((meter) => meter?.name),
  );
  form$: Observable<FormGroup>;
  basetreesConnections$: Observable<readonly BasetreeConnectionsViewModel[]>;
  resetDisabled$: Observable<boolean>;
  saveDisabled$: Observable<boolean>;

  private formInitValue$ = this._store.pipe(
    select(DataSelectors.basetrees.getList),
    filter((basetrees) => !isEmpty(basetrees)),
    take(1),
    switchMap((basetrees) =>
      this._store.pipe(
        select(fromMeterManagement.getSelectedMeterNormalized),
        notNull(),
        take(1),
        map((meter) => ({
          name: meter.name,
          measureId: meter.measureId,
          basetrees: getConnectionPerBasetree(meter, basetrees),
        })),
      ),
    ),
    shareReplay({ refCount: true, bufferSize: 1 }),
  );

  ngOnInit(): void {
    this.initForm();
    this.basetreesConnections$ = this.getBasetreesConnections();
    this.handleRouteChange();
  }

  ngOnDestroy(): void {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }

  onEditMeterConfigs() {
    this._store
      .pipe(
        select(MetersListSelectors.getSelectedId),
        take(1),
        notNull(),
        map((id) => MeterMgmtActions.configEditor.openConfigGraphEditor({ id })),
      )
      .subscribe(this._store);
  }

  onEdit({ basetrees, ...meter }: any) {
    this._store
      .pipe(
        select(fromMeterManagement.getSelectedMeterNormalized),
        map((originalMeter) =>
          DataActions.meters.update({
            meter: { ...diffObject(meter, originalMeter), id: originalMeter.id },
            basetrees,
            originalMeter,
          }),
        ),
        takeUntil(this.unsubscribe$),
        take(1),
      )
      .subscribe(this._store);
  }

  resetForm() {
    this.form$
      .pipe(take(1), withLatestFrom(this.formInitValue$), takeUntil(this.unsubscribe$))
      .subscribe(([form, meter]) => form.reset(meter));
  }

  private initForm() {
    this.form$ = this.formInitValue$.pipe(
      map((formMeter) =>
        this._fb.group({
          name: [formMeter.name, [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
          measureId: [formMeter.measureId, Validators.required],
          basetrees: this._fb.group(formMeter.basetrees),
        }),
      ),
      shareReplay({ refCount: true, bufferSize: 1 }),
    );

    this.resetDisabled$ = this.form$.pipe(
      take(1),
      switchMap((form) =>
        form.statusChanges.pipe(
          startWith(<string>form.status),
          map(() => !form.dirty),
        ),
      ),
    );

    this.saveDisabled$ = this.form$.pipe(
      take(1),
      switchMap((form) =>
        form.statusChanges.pipe(
          startWith(<string>form.status),
          map(() => !(form.valid && form.dirty)),
        ),
      ),
    );
  }

  private handleRouteChange() {
    this._route.paramMap
      .pipe(
        map((params) => params.get('id')),
        map((id) => MeterMgmtActions.meterEditor.openMeterEditorSuccess({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this._store);
  }

  private getBasetreesConnections() {
    return combineLatest([
      this._store.pipe(select(DataSelectors.nodes.getNodesPerBasetree)),
      this._store.pipe(select(DataSelectors.basetrees.getEntities)),
      this._store.pipe(select(DataSelectors.nodes.getEntities)),
      this.form$.pipe(
        notNull(),
        take(1),
        switchMap((form) => {
          const basetreesControl = form.get('basetrees') as FormControl;
          return basetreesControl.valueChanges.pipe(startWith<Dict<Id>>(<Dict<Id>>basetreesControl.value));
        }),
      ),
    ]).pipe(
      map(([treeNodesPerBasetree, basetrees, treeNodes, formBasetrees]) =>
        generateBasetreeConnections(treeNodesPerBasetree, basetrees, treeNodes, formBasetrees),
      ),
    );
  }

  constructor(
    private _store: Store<fromMeterManagement.State>,
    private _route: ActivatedRoute,
    private _fb: FormBuilder,
  ) {}
}
