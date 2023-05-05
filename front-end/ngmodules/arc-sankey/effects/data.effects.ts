import { of } from 'rxjs';
import { catchError, filter, map, mapTo, switchMap, switchMapTo, withLatestFrom } from 'rxjs/operators';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { Injectable } from '@angular/core';
import { select, Store } from '@ngrx/store';
import { endDateConfig } from '../../energy-insight/reducers/_config';
import * as fromSankey from '../reducers';
import { parseISO } from 'date-fns';
import { LoaderService } from '@core/services/loader.service';
import { ArcSankeyActions } from '../actions';
import { ArcSankeyService } from '../services/arc-sankey.service';
import { ArcSankeySelectors } from '../selectors';

@Injectable()
export class DataEffects {
  loadConfigRequest$ = createEffect(() =>
    this.loader.onceForDomainFromRoute('/app/arc-sankey').pipe(mapTo(ArcSankeyActions.filter.loadConfig())),
  );

  loadConfig$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ArcSankeyActions.filter.loadConfig),
      switchMapTo(
        this.arcSankeyService.loadConfig().pipe(
          map(ArcSankeyActions.filter.loadConfigSuccess),
          catchError((err) => of(ArcSankeyActions.filter.loadConfigFail({ message: err.message || err }))),
        ),
      ),
    ),
  );

  loadSankeyDataOnFilterChange$ = createEffect(() =>
    this.actions$.pipe(
      ofType(
        ArcSankeyActions.filter.selectStartDate,
        ArcSankeyActions.filter.selectPeriod,
        ArcSankeyActions.filter.selectSite,
        ArcSankeyActions.filter.incrementDate,
        ArcSankeyActions.filter.decrementDate,
      ),
      withLatestFrom(
        this.store.pipe(select(ArcSankeySelectors.filter.getSiteId)),
        this.store.pipe(select(ArcSankeySelectors.filter.getStartDate)),
        this.store.pipe(select(ArcSankeySelectors.filter.getSelectedPeriod)),
      ),
      filter(([, siteId]) => siteId != null),
      map(([, siteId, startDate, period]) =>
        ArcSankeyActions.data.load({ siteId, startDate: startDate.toISOString(), period }),
      ),
    ),
  );

  loadSankeyData$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ArcSankeyActions.data.load),
      switchMap(({ period, siteId, startDate: startDateIso }) => {
        const startDate = parseISO(startDateIso);
        const endDate = endDateConfig[period](startDate);
        return this.arcSankeyService.loadData(siteId, startDate, endDate, period).pipe(
          map(ArcSankeyActions.data.loadSuccess),
          catchError((err) => of(ArcSankeyActions.data.loadFail({ message: err.message || err }))),
        );
      }),
    ),
  );

  constructor(
    private actions$: Actions,
    private store: Store<fromSankey.State>,
    private arcSankeyService: ArcSankeyService,
    private loader: LoaderService,
  ) {}
}
