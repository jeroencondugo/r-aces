import { of } from 'rxjs';
import { catchError, filter, map, switchMap, withLatestFrom } from 'rxjs/operators';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Injectable } from '@angular/core';
import { HeatmapActions } from '../actions';
import { HeatmapService } from '../services/heatmap.service';
import { Dict, notNull } from '@shared/utils/common.utils';
import { select, Store } from '@ngrx/store';
import * as fromRoot from '@core/reducers';
import { HeatmapSelectors } from '../selectors';
import { Id } from '@shared/models/id.model';
import { HeatmapConfig } from '../models/heatmap.model';

@Injectable()
export class FilterEffects {
  loadConfigRequest$ = createEffect(() =>
    this.actions$.pipe(
      ofType(HeatmapActions.filter.selectMeasure),
      map(({ measure }) => measure),
      notNull(),
      withLatestFrom(this.store.pipe(select(HeatmapSelectors.filter.getConfigsPerMeasure))),
      filter(configNotLoaded),
      map(([measure]) => HeatmapActions.filter.loadConfig({ measure })),
    ),
  );

  loadConfig$ = createEffect(() =>
    this.actions$.pipe(
      ofType(HeatmapActions.filter.loadConfig),
      switchMap(({ measure }) =>
        this.heatmapService.loadConfig(measure).pipe(
          map((config) => HeatmapActions.filter.loadConfigSuccess({ config })),
          catchError((err) => of(HeatmapActions.filter.loadConfigFail({ message: err.message || err }))),
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

function configNotLoaded([measure, configsPerMeasure]: [Id, Dict<HeatmapConfig>]) {
  return configsPerMeasure[measure] == null;
}
