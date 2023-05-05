import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { select, Store } from '@ngrx/store';
import { filter, map, mapTo, withLatestFrom } from 'rxjs/operators';

import * as fromRoot from '@core/reducers';
import * as fromMeterManagement from '../reducers';
import { NavigationActions } from '@core/actions';
import { MeterMgmtActions } from '../actions';
import { MetersListSelectors } from '../selectors';
import { hasId } from '@shared/utils/common.utils';
import { DataActions } from '@data/actions';
import { isSubRoute } from '@shared/utils/rxjs.utils';

const isMeterMgmtRoute = (route: string) => isSubRoute('/app/meter-mgmt', route);

@Injectable()
export class MetersListEffects {
  openMeterDetail$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.metersList.selectId),
      map(({ id }) => NavigationActions.go({ path: [`/app/meter-mgmt`, id] })),
    ),
  );

  selectMeterOnCreateSuccess$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.addSuccess, DataActions.meters.updateSuccess),
      withLatestFrom(this.store.pipe(select(fromRoot.selectUrl))),
      filter(([, route]) => isMeterMgmtRoute(route)),
      map(([{ meter }]) => MeterMgmtActions.metersList.selectId(meter)),
    ),
  );

  selectPageOnCreateSuccess$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.addSuccess, DataActions.meters.updateSuccess),
      withLatestFrom(
        this.store.pipe(select(fromMeterManagement.getMetersFilteredCollection)),
        this.store.pipe(select(MetersListSelectors.getPageSize)),
        this.store.pipe(select(fromRoot.selectUrl)),
      ),
      filter(([, , , route]) => isMeterMgmtRoute(route)),
      map(([{ meter }, meters, pageSize]) => {
        const focusIndex = Math.max(0, meters.findIndex(hasId(meter.id)));
        const selectedPage = Math.floor(focusIndex / pageSize);
        return MeterMgmtActions.metersList.selectPage({ page: selectedPage });
      }),
    ),
  );

  navigateFromDeletedMeter$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.removeSuccess),
      withLatestFrom(this.store.pipe(select(MetersListSelectors.getSelectedId))),
      filter(([{ id }, selectedId]) => id === selectedId || selectedId == null),
      mapTo(NavigationActions.goToUrl({ url: '/app/meter-mgmt/' })),
    ),
  );

  constructor(private actions$: Actions, private store: Store<fromMeterManagement.State>) {}
}
