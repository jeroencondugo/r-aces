import { combineLatest, of, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, map, takeUntil } from 'rxjs/operators';
import { ChangeDetectionStrategy, Component, OnDestroy, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { PageEvent } from '@angular/material/paginator';
import { select, Store } from '@ngrx/store';

import * as fromRoot from '@core/reducers';
import * as fromMeterManagement from '../../reducers';
import { MeterMgmtActions } from '../../actions';
import { Id } from '@shared/models/id.model';
import { MetersListSelectors } from '../../selectors';
import { DataSelectors } from '@data/selectors';

@Component({
  selector: 'cdg-meter-management',
  styleUrls: ['./meter-management.component.scss'],
  templateUrl: './meter-management.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MeterManagementComponent implements OnInit, OnDestroy {
  private _destroy$ = new Subject();

  searchTermControl: FormControl = new FormControl('');
  meterList$ = this._store.pipe(select(fromMeterManagement.getVisibleMeters));
  displayedColumns$ = of(['name', 'meterType', 'commodityType', 'site']);
  metersSorting$ = this._store.pipe(select(MetersListSelectors.getSortingArray));
  selectedMeterId$ = this._store.pipe(select(MetersListSelectors.getSelectedId));
  selectedPage$ = this._store.pipe(select(fromMeterManagement.getSelectedPageClamp));
  pageSize$ = this._store.pipe(select(MetersListSelectors.getPageSize));
  loading$ = this._store.pipe(select(DataSelectors.meters.getLoading));

  filteredMetersCount$ = this._store.pipe(
    select(fromMeterManagement.getMetersFilteredCollection),
    map((meters) => meters?.length ?? 0),
  );

  filterHint$ = combineLatest([
    this._store.pipe(select(DataSelectors.meters.getCount)),
    this.filteredMetersCount$,
  ]).pipe(
    map(([total, filtered]) =>
      total - filtered > 0
        ? total > 0 && filtered > 0
          ? `Displaying ${filtered} / ${total} meters`
          : `No meters found. Narrow down the search`
        : '',
    ),
  );

  ngOnInit() {
    this.searchTermControl.valueChanges
      .pipe(
        takeUntil(this._destroy$),
        debounceTime(200),
        distinctUntilChanged(),
        map((searchTerm) => MeterMgmtActions.metersList.searchMeters({ searchTerm })),
      )
      .subscribe(this._store);

    this._store.pipe(takeUntil(this._destroy$), select(MetersListSelectors.getSearchTerm)).subscribe((searchTerm) =>
      this.searchTermControl.patchValue(searchTerm, {
        onlySelf: true,
        emitEvent: false,
        emitModelToViewChange: true,
      }),
    );
  }

  onMeterIdSelected(id: Id) {
    this._store.dispatch(MeterMgmtActions.metersList.selectId({ id }));
  }

  onSearch(searchTerm: string) {
    this._store.dispatch(MeterMgmtActions.metersList.searchMeters({ searchTerm }));
  }

  onCreateMeter() {
    this._store.dispatch(MeterMgmtActions.meterEditor.openNewMeterDialog());
  }

  onPageSelected(event: PageEvent) {
    this._store.dispatch(MeterMgmtActions.metersList.selectPage({ page: event.pageIndex }));
  }

  ngOnDestroy(): void {
    this._destroy$.next();
  }

  onMetersSingleSort(column: string) {
    this._store.dispatch(MeterMgmtActions.metersList.sortMeters({ column }));
  }

  onMetersMultiSort(column: string) {
    this._store.dispatch(MeterMgmtActions.metersList.multiSortMeters({ column }));
  }

  constructor(private _store: Store<fromRoot.State>) {}
}
