import { map, scan, take } from 'rxjs/operators';
import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { select, Store } from '@ngrx/store';
import { combineLatest, Observable, ReplaySubject, Subject } from 'rxjs';
import * as fromRoot from '@core/reducers';

import { isPeriod, isResolution } from '@shared/models/filters';
import { HeatmapSelectors } from '../../selectors';
import { HeatmapActions } from '../../actions';
import { MatSelectChange } from '@angular/material/select';
import { Id } from '@shared/models/id.model';
import { exactlyOne } from '@shared/utils/array.utils';
import { MatOption } from '@angular/material/core';
import { Nullable } from '@shared/types/nullable.type';
import { Tile } from '@components/heatmap/heatmap.model';
import { Dict } from '@shared/utils/common.utils';

@Component({
  selector: 'cdg-cluster-heatmap-container',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './heatmap.container.html',
  styleUrls: ['./heatmap.container.scss'],
})
export class HeatmapContainer implements OnDestroy {
  private unsubscribe$ = new Subject();
  private _selectedValue$ = new ReplaySubject<{ id: Id; value: Nullable<number> }>(1);
  selectedValue$: Observable<Dict<number, Id>> = this._selectedValue$.pipe(
    scan((agg, { value, id }) => ({ ...agg, [id]: value }), <Dict<Nullable<number>>>{}),
  );

  measures$ = this.store.pipe(select(HeatmapSelectors.measures.getAvailable));
  selectedMeasure$ = this.store.pipe(select(HeatmapSelectors.filter.getMeasureId));
  heatmaps$ = this.store.pipe(select(HeatmapSelectors.data.getHeatmaps));
  heatmapsLoading$ = this.store.pipe(select(HeatmapSelectors.data.getLoading));
  availablePeriods$ = this.store.pipe(select(HeatmapSelectors.filter.getAvailablePeriods));
  selectedPeriod$ = this.store.pipe(select(HeatmapSelectors.filter.getSelectedPeriod));
  availableResolutions$ = this.store.pipe(select(HeatmapSelectors.filter.getAvailableResolutions));
  selectedResolution$ = this.store.pipe(select(HeatmapSelectors.filter.getSelectedResolution));
  datetimeOptions$ = this.store.pipe(select(HeatmapSelectors.filter.getDatetimeOptions));
  startDate$ = this.store.pipe(select(HeatmapSelectors.filter.getStartDate));
  previousDisabled$ = this.store.pipe(select(HeatmapSelectors.filter.getPreviousDateDisabled));
  nextDisabled$ = this.store.pipe(select(HeatmapSelectors.filter.getNextDateDisabled));
  periodDisabled$ = this.availablePeriods$.pipe(map(exactlyOne));
  resolutionDisabled$ = this.availableResolutions$.pipe(map(exactlyOne));
  minDate$ = this.store.pipe(select(HeatmapSelectors.filter.getMinDate));
  maxDate$ = this.store.pipe(select(HeatmapSelectors.filter.getMaxDate));
  availableMeters$ = this.store.pipe(select(HeatmapSelectors.meters.getAvailableMeters));

  displayFilterActions$ = combineLatest([
    this.store.pipe(select(HeatmapSelectors.meters.getHasAvailableMeters)),
    this.store.pipe(select(HeatmapSelectors.filter.getConfig)),
  ]).pipe(map(([hasMeters, config]) => hasMeters && config != null));

  onChangeStartDate(date: Date) {
    this.store.dispatch(HeatmapActions.filter.selectStartDate({ date: date.toISOString() }));
  }

  onIncrementStartDate() {
    this.startDate$
      .pipe(
        take(1),
        map((date) => HeatmapActions.filter.incrementDate({ date: date.toISOString() })),
      )
      .subscribe(this.store);
  }

  onDecrementStartDate() {
    this.startDate$
      .pipe(
        take(1),
        map((date) => HeatmapActions.filter.decrementDate({ date: date.toISOString() })),
      )
      .subscribe(this.store);
  }

  selectMeasure({ value }: MatSelectChange) {
    const measure = value as Id;
    this.store.dispatch(HeatmapActions.filter.selectMeasure({ measure }));
  }

  selectPeriod({ value: period }: MatSelectChange) {
    if (isPeriod(period)) {
      this.store.dispatch(HeatmapActions.filter.selectPeriod({ period }));
    }
  }

  selectResolution({ value: resolution }: MatSelectChange) {
    if (isResolution(resolution)) {
      this.store.dispatch(HeatmapActions.filter.selectResolution({ resolution }));
    }
  }

  selectDemandMeters(selected: MatOption | MatOption[]) {
    this.store.dispatch(HeatmapActions.meters.selectDemand({ selection: toSelection(selected) }));
  }

  selectExcessMeters(selected: MatOption | MatOption[]) {
    this.store.dispatch(HeatmapActions.meters.selectExcess({ selection: toSelection(selected) }));
  }

  ngOnDestroy(): void {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
    this._selectedValue$.complete();
    this.store.dispatch(HeatmapActions.data.clear());
  }

  onTileSelected(id: Id, tile: Nullable<Tile>) {
    this._selectedValue$.next({ id, value: tile?.value });
  }

  constructor(private store: Store<fromRoot.State>) {}
}

function toSelection(selected: MatOption | MatOption[]) {
  const selection = Array.isArray(selected) ? selected.map(({ value }) => value as Id) : [selected.value as Id];
  return selection;
}
