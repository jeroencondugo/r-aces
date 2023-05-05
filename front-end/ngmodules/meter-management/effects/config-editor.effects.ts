import { of } from 'rxjs';
import { catchError, filter, map, mapTo, switchMap, withLatestFrom } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType, OnInitEffects } from '@ngrx/effects';

import { MeterManagementService } from '@core/services/meter-management.service';
import { AppActions, LocalStorageActions, NavigationActions, NotificationsActions } from '@core/actions';
import { MeterMgmtActions } from '../actions';
import { Action, select, Store } from '@ngrx/store';
import * as fromRoot from '@core/reducers';
import { ConfigEditorSelectors } from '../selectors';

const NAVIGATION_HISTORY_KEY = 'config_nav_history';

@Injectable()
export class ConfigEditorEffects implements OnInitEffects {
  openConfigGraphEditor$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.openConfigGraphEditor),
      map(({ id }) => NavigationActions.go({ path: ['app/meter-mgmt/config/', id] })),
    ),
  );

  closeConfigGraphEditor$ = createEffect(() =>
    this.actions$.pipe(ofType(MeterMgmtActions.configEditor.navigateBack), mapTo(NavigationActions.back())),
  );

  loadMeterConfigs$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.openConfigGraphEditorSuccess),
      switchMap(({ id }) =>
        this.meterManagementService.loadConfigs(id).pipe(
          map((response) => MeterMgmtActions.configEditor.loadConfigSuccess(response)),
          catchError((err) => of(MeterMgmtActions.configEditor.loadConfigFail({ error: err.message || err }))),
        ),
      ),
    ),
  );

  saveEditorChanges$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.saveChanges),
      switchMap(({ changes }) =>
        this.meterManagementService.saveChanges(changes).pipe(
          map((response) => MeterMgmtActions.configEditor.saveChangesSuccess(response)),
          catchError((err) => of(MeterMgmtActions.configEditor.saveChangesFail({ error: err.message || err }))),
        ),
      ),
    ),
  );

  undoLastChangeOnGenerateLayoutError$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.generateLayoutFailed),
      filter(({ hasChanges }) => hasChanges),
      mapTo(MeterMgmtActions.configEditor.undoChange()),
    ),
  );

  runTests$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.runTests),
      switchMap(({ meterId }) =>
        this.meterManagementService.runTests(meterId).pipe(
          map(
            (dataResults) => MeterMgmtActions.configEditor.runTestsSuccess({ meterId, dataResults }),
            catchError((err) => of(MeterMgmtActions.configEditor.runTestsFail({ message: err.message ?? err }))),
          ),
        ),
      ),
    ),
  );

  saveHistoryOnExit$ = createEffect(() =>
    this.actions$.pipe(
      ofType(AppActions.close),
      withLatestFrom(this.store.pipe(select(ConfigEditorSelectors.getNavigationHistoryIds))),
      map(([, ids]) => LocalStorageActions.save({ value: ids.join(','), key: NAVIGATION_HISTORY_KEY })),
    ),
  );

  historyFromPersistence$ = createEffect(() =>
    this.actions$.pipe(
      ofType(LocalStorageActions.loadSuccess),
      filter(({ key, value }) => key === NAVIGATION_HISTORY_KEY && !!value),
      map(({ value }) => value.split(',')),
      map((navigationHistory) => MeterMgmtActions.configEditor.historyFromCache({ navigationHistory })),
    ),
  );

  onLoadCreateConfig$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.loadCreateConfig),
      switchMap(({ config, meta: inputMeta }) =>
        this.meterManagementService.loadCreateConfig(config, inputMeta).pipe(
          map((meta) => MeterMgmtActions.configEditor.loadCreateConfigSuccess({ config, meta })),
          catchError((err) => of(MeterMgmtActions.configEditor.loadCreateConfigFail({ error: err.message || err }))),
        ),
      ),
    ),
  );

  onLoadEditConfig$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.loadEditConfig),
      switchMap(({ oldConfig, newConfig }) =>
        this.meterManagementService.loadEditConfig(oldConfig, newConfig).pipe(
          map((config) => MeterMgmtActions.configEditor.loadEditConfigSuccess({ config })),
          catchError((err) => of(MeterMgmtActions.configEditor.loadEditConfigFail({ error: err.message || err }))),
        ),
      ),
    ),
  );

  /** LOGGERS **/
  logInvalidEditorAction$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.generateLayoutFailed),
      map(({ hasChanges, error }) =>
        NotificationsActions.error({
          text: error,
          title: hasChanges ? 'Invalid operation' : 'Invalid data',
        }),
      ),
    ),
  );

  logSaveChangesFail$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.saveChangesFail),
      map(({ error }) =>
        NotificationsActions.error({
          text: error,
          title: 'Save changes failed',
        }),
      ),
    ),
  );

  saveChangesSuccess$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.configEditor.saveChangesSuccess),
      map(() => NotificationsActions.success({ text: `Saved!`, title: `Save changes success!` })),
    ),
  );

  ngrxOnInitEffects(): Action {
    return LocalStorageActions.load({ key: NAVIGATION_HISTORY_KEY });
  }

  constructor(
    private actions$: Actions,
    private meterManagementService: MeterManagementService,
    private store: Store<fromRoot.State>,
  ) {}
}
