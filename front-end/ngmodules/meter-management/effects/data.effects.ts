import { of } from 'rxjs';
import { catchError, filter, map, mapTo, switchMap, switchMapTo } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';

import { MeterManagementService } from '@core/services/meter-management.service';
import { DialogService } from '@core/services/dialog.service';
import { NotificationsActions } from '@core/actions';
import { LoaderService } from '@core/services/loader.service';
import { MeterMgmtActions } from '../actions';
import { DataActions } from '@data/actions';

@Injectable()
export class DataEffects {
  loadMeterConfigsCatalogRequest$ = createEffect(() =>
    this.loader
      .onceForDomainFromRoute('/app/meter-mgmt/config')
      .pipe(mapTo(MeterMgmtActions.data.loadMeterConfigsCatalog())),
  );

  loadMeterConfigsCatalog$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.data.loadMeterConfigsCatalog),
      switchMapTo(
        this.meterManagementService.loadConfigsCatalog().pipe(
          map((catalog) => MeterMgmtActions.data.loadMeterConfigsCatalogSuccess({ catalog })),
          catchError((err) => of(MeterMgmtActions.data.loadMeterConfigsCatalogFail({ error: err.message || err }))),
        ),
      ),
    ),
  );

  confirmDeleteMeter$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.data.confirmDeleteMeter),
      switchMap(({ meter }) =>
        this.messageBox
          .danger('Delete meter', `Are you sure you want to delete meter '${meter.name || meter.id}'`, 'Delete')
          .pipe(
            filter((confirmed) => confirmed === true),
            mapTo(DataActions.meters.remove(meter)),
          ),
      ),
    ),
  );

  // LOGGERS
  logDeleteMeterFail$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.removeFail),
      map(({ error }) => NotificationsActions.error({ text: error, title: 'Delete meter failed' })),
    ),
  );

  logCreateMeterSuccess$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.addSuccess),
      map(({ meter }) =>
        NotificationsActions.success({
          text: `Meter '${meter.name} [id ${meter.id}]' created successfully`,
          title: 'Meter Management',
        }),
      ),
    ),
  );

  logDeleteMeterSuccess$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.removeSuccess),
      map(({ id }) =>
        NotificationsActions.success({ text: `Meter ID: ${id} has been deleted`, title: 'Meter Deleted' }),
      ),
    ),
  );

  logCreateMeterFail$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DataActions.meters.addFail),
      map(({ error }) => NotificationsActions.error({ text: error, title: 'Create meter failed' })),
    ),
  );

  constructor(
    private actions$: Actions,
    private meterManagementService: MeterManagementService,
    private messageBox: DialogService,
    private loader: LoaderService,
  ) {}
}
