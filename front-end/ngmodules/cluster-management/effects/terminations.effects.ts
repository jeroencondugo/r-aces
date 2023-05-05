import { Injectable } from '@angular/core';
import { of } from 'rxjs';
import { catchError, filter, map, mergeMap, switchMap } from 'rxjs/operators';
import { Actions, createEffect, ofType } from '@ngrx/effects';

import { NavigationActions, NotificationsActions } from '@core/actions';
import { LoaderService } from '@core/services/loader.service';
import { TerminationActions } from '../actions';
import { TerminationsService } from '../servlces/terminations.service';

@Injectable()
export class TerminationEffects {
  initTerminations$ = createEffect(() =>
    this.loader.onceForDomainFromRoute('/app/cluster-mgmt/terminations').pipe(map(() => TerminationActions.load())),
  );

  loadTerminations$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.load),
      switchMap(() =>
        this.service.load().pipe(
          map((terminations) => TerminationActions.loadSuccess({ terminations })),
          catchError((err) => of(TerminationActions.loadFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  selectTermination$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.select),
      map(({ id }) => NavigationActions.go({ path: [`/app/cluster-mgmt/terminations/${id}`] })),
    ),
  );

  createTermination$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.create),
      mergeMap(({ termination }) =>
        this.service.create(termination).pipe(
          map((terminations) => TerminationActions.createSuccess({ terminations })),
          catchError((err) => of(TerminationActions.createFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  createTerminationSuccess$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.createSuccess),
      map(() => NotificationsActions.success({ text: 'Terminations requested', title: 'Termination status' })),
    ),
  );

  removeTermination$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.remove),
      mergeMap(({ id }) =>
        this.service.delete(id).pipe(
          map(([termination]) => TerminationActions.removeSuccess({ termination })),
          catchError((err) => of(TerminationActions.removeFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  acceptTermination$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.accept),
      mergeMap(({ id }) =>
        this.service.accept(id).pipe(
          map((termination) => TerminationActions.acceptSuccess({ termination })),
          catchError((err) => of(TerminationActions.acceptFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  acceptedTermination$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.acceptSuccess),
      map(() => NotificationsActions.success({ text: `Accepted termination`, title: 'Termination Answer' })),
    ),
  );

  acceptedTerminationFail$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.acceptFail),
      map(() => NotificationsActions.error({ text: `Failed to accept termination`, title: 'Termination Answer' })),
    ),
  );

  declineTermination$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.decline),
      mergeMap(({ id }) =>
        this.service.decline(id).pipe(
          map((termination) => TerminationActions.declineSuccess({ termination })),
          catchError((err) => of(TerminationActions.declineFail({ msg: err || err?.message }))),
        ),
      ),
    ),
  );

  declinedInvite$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.declineSuccess),
      map(() => NotificationsActions.success({ text: `Declined termination`, title: 'Termination Answer' })),
    ),
  );

  declinedInviteFail$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.declineFail),
      map(() => NotificationsActions.error({ text: `Failed to decline termination`, title: 'Termination Answer' })),
    ),
  );

  afterEdit$ = createEffect(() =>
    this.actions$.pipe(
      ofType(TerminationActions.createSuccess),
      filter(({ terminations }) => terminations.length > 0),
      map(({ terminations }) => TerminationActions.select({ id: terminations[0].id })),
    ),
  );

  constructor(private loader: LoaderService, private actions$: Actions, private service: TerminationsService) {}
}
