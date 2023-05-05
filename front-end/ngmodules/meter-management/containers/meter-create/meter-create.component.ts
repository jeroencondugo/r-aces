import { combineLatest, Observable, ReplaySubject, Subject } from 'rxjs';
import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { select, Store } from '@ngrx/store';
import * as fromMeterManagement from '../../reducers';
import { Dict, isEmpty } from '@shared/utils/common.utils';
import { filter, map, startWith, take, takeUntil } from 'rxjs/operators';
import { DataSelectors } from '@data/selectors';
import { commonAnimations } from '@shared/animations';
import { DataActions } from '@data/actions';
import { BasetreeConnectionsViewModel } from '@shared/models/meters';
import { generateBasetreeConnections } from '@shared/utils/meter.utils';
import { Id } from '@shared/models/id.model';

@Component({
  selector: 'cdg-meter-create',
  animations: [commonAnimations.fadeAnimation],
  templateUrl: './meter-create.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MeterCreateComponent implements OnDestroy {
  private unsubscribe$ = new Subject();
  private resetForm$ = new ReplaySubject<boolean>(1);

  private basetrees$ = this._store.pipe(select(DataSelectors.basetrees.getList));
  form: FormGroup;
  measures$ = this._store.pipe(select(DataSelectors.measures.getAll));
  basetreesConnections$: Observable<readonly BasetreeConnectionsViewModel[]>;

  private get basetreesFormGroup() {
    const basetrees = this.form.get('basetrees');
    return basetrees as FormGroup;
  }

  constructor(private _fb: FormBuilder, private _store: Store<fromMeterManagement.State>) {
    this.form = this._fb.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      measureId: [null, Validators.required],
      basetrees: this._fb.group({}),
    });

    this.basetrees$
      .pipe(
        takeUntil(this.unsubscribe$),
        filter((basetrees) => !isEmpty(basetrees)),
        take(1),
      )
      .subscribe((basetrees) => {
        const formArray = this.basetreesFormGroup;
        Object.keys(formArray.controls).forEach((key) => formArray.removeControl(key));
        basetrees.forEach((_basetree) => formArray.registerControl(_basetree.id.toString(), new FormControl(null)));
      });

    this.basetreesConnections$ = combineLatest([
      this._store.pipe(select(DataSelectors.nodes.getNodesPerBasetree)),
      this._store.pipe(select(DataSelectors.basetrees.getEntities)),
      this._store.pipe(select(DataSelectors.nodes.getEntities)),
      this.basetreesFormGroup.valueChanges.pipe(startWith<Dict<Id>>(<Dict<Id>>this.basetreesFormGroup.value)),
    ]).pipe(
      map(([basetreeConnections, basetrees, treeNodes, formBasetrees]) =>
        generateBasetreeConnections(basetreeConnections, basetrees, treeNodes, formBasetrees),
      ),
    );

    this.resetForm$.pipe(takeUntil(this.unsubscribe$)).subscribe(() => {
      this.form.reset();
    });
  }

  ngOnDestroy(): void {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
    this.resetForm$.complete();
  }

  onCreate(formMeter: any) {
    const { basetrees, ...meter } = formMeter;
    this.resetForm();
    this._store.dispatch(DataActions.meters.add({ meter, basetrees }));
  }

  resetForm() {
    this.resetForm$.next();
  }
}
