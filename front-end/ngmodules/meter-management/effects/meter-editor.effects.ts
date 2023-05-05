import { map, mapTo } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';

import { NavigationActions } from '@core/actions';
import { MeterMgmtActions } from '../actions';

@Injectable()
export class MeterEditorEffects {
  openNewMeterDialog$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.meterEditor.openNewMeterDialog),
      mapTo(NavigationActions.goToUrl({ url: '/app/meter-mgmt/new' })),
    ),
  );

  openMeterEditor$ = createEffect(() =>
    this.actions$.pipe(
      ofType(MeterMgmtActions.meterEditor.openMeterEditor),
      map(({ id }) => NavigationActions.go({ path: [`/app/meter-mgmt/edit`, id] })),
    ),
  );

  constructor(private actions$: Actions) {}
}
