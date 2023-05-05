import { combineLatest } from 'rxjs';
import { filter, map, mapTo, switchMap, switchMapTo, take, withLatestFrom } from 'rxjs/operators';
import { Actions, createEffect, ofType, OnInitEffects } from '@ngrx/effects';
import { Injectable } from '@angular/core';
import { Action, select, Store } from '@ngrx/store';

import { hasId, notNull } from '@shared/utils/common.utils';
import { DataSelectors } from '@data/selectors';
import { AppActions, DomainLocalStorageActions } from '@core/actions';
import { ArcSankeyActions } from '../actions';
import { ArcSankeySelectors } from '../selectors';
import * as fromRoot from '@core/reducers';

@Injectable()
export class FilterEffects implements OnInitEffects {
  onInit$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ArcSankeyActions.module.init),
      mapTo(DomainLocalStorageActions.load({ key: 'arc-sankey.siteId' })),
    ),
  );

  selectSiteOnInit$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ArcSankeyActions.filter.siteIdFromCache),
      switchMap(({ id: cachedId }) =>
        combineLatest([this.sitesLoaded(), this.configLoaded()]).pipe(
          withLatestFrom(this.store.pipe(select(ArcSankeySelectors.sites.getList))),
          map(([, sites = []]) => {
            const id = sites.some(hasId(cachedId)) ? +cachedId : sites[0]?.id;
            return ArcSankeyActions.filter.selectSite({ id });
          }),
          take(1),
        ),
      ),
    ),
  );

  saveSelectedSiteOnExit$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AppActions.close),
      switchMapTo(this.store.pipe(select(ArcSankeySelectors.filter.getSiteId))),
      notNull(),
      map((siteId) => DomainLocalStorageActions.save({ key: 'arc-sankey.siteId', value: siteId.toString() })),
    ),
  );

  siteIdLoadedFromCache$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DomainLocalStorageActions.loadSuccess),
      filter(({ key }) => key === 'arc-sankey.siteId'),
      map(({ value }) => value),
      map((id) => ArcSankeyActions.filter.siteIdFromCache({ id })),
    ),
  );

  ngrxOnInitEffects(): Action {
    return ArcSankeyActions.module.init();
  }

  private sitesLoaded() {
    return this.store.pipe(
      select(DataSelectors.sites.getLoaded),
      filter((loaded) => loaded),
      take(1),
    );
  }

  private configLoaded() {
    return this.store.pipe(
      select(ArcSankeySelectors.filter.getConfigsLoaded),
      filter((loaded) => loaded),
      take(1),
    );
  }

  constructor(private actions$: Actions, private store: Store<fromRoot.State>) {}
}
