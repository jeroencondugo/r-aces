import { of } from 'rxjs';
import { catchError, filter, map, switchMap, withLatestFrom } from 'rxjs/operators';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Injectable } from '@angular/core';
import { HeatmapActions } from '../actions';
import { HeatmapService } from '../services/heatmap.service';
import { HeatmapSelectors } from '../selectors';
import { select, Store } from '@ngrx/store';

import * as fromRoot from '@core/reducers';

@Injectable()
export class DataEffects {
  loadDataOnFilterChange$ = createEffect(() =>
    this.actions$.pipe(
      ofType(
        HeatmapActions.filter.selectStartDate,
        HeatmapActions.filter.selectPeriod,
        HeatmapActions.filter.selectResolution,
        HeatmapActions.filter.incrementDate,
        HeatmapActions.filter.decrementDate,
        HeatmapActions.meters.selectExcess,
        HeatmapActions.meters.selectDemand,
      ),
      withLatestFrom(
        this.store.pipe(select(HeatmapSelectors.meters.getSelectedDemandMeters)),
        this.store.pipe(select(HeatmapSelectors.meters.getSelectedExcessMeters)),
        this.store.pipe(select(HeatmapSelectors.filter.getQueryParams)),
      ),
      filter(([_action, demand, excess]) => demand?.length > 0 || excess?.length > 0),
      map(([_action, demand, excess, params]) => HeatmapActions.data.load({ excess, demand, ...params })),
    ),
  );

  loadData$ = createEffect(() =>
    this.actions$.pipe(
      ofType(HeatmapActions.data.load),
      switchMap((payload) =>
        this.heatmapService.loadData(payload).pipe(
          map((heatmaps) => HeatmapActions.data.loadSuccess({ heatmaps })),
          catchError((err) => of(HeatmapActions.data.loadFail({ message: err.message || err }))),
        ),
      ),
    ),
  );

  constructor(
    private store: Store<fromRoot.State>,
    private actions$: Actions,
    private heatmapService: HeatmapService,
  ) {}
}
