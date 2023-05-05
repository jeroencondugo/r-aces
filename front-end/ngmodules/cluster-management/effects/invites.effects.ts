import { Injectable } from '@angular/core';
import { of } from 'rxjs';
import { catchError, filter, map, mapTo, mergeMap, switchMap, withLatestFrom } from 'rxjs/operators';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { select, Store } from '@ngrx/store';

import { NavigationActions, NotificationsActions } from '@core/actions';
import { State } from '@core/reducers';
import { LoaderService } from '@core/services/loader.service';
import { InviteActions } from '../actions';
import { InvitesService } from '../servlces/invites.service';
import { ClusterManagementSelectors } from '../selectors';

@Injectable()
export class InviteEffects {
  initInvites$ = createEffect(() =>
    this.loader.onceForDomainFromRoute('/app/cluster-mgmt/invites').pipe(mapTo(InviteActions.load())),
  );

  loadInvites$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.load),
      switchMap(() =>
        this.service.load().pipe(
          map((invites) => InviteActions.loadSuccess({ invites })),
          catchError((err) => of(InviteActions.loadFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  selectInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.select),
      map(({ id }) => NavigationActions.go({ path: [`app/cluster-mgmt/invites/${id}`] })),
    ),
  );

  createInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.create),
      mergeMap(({ invite }) =>
        this.service.create(invite).pipe(
          map((invites) => InviteActions.createSuccess({ invites })),
          catchError((error) => of(InviteActions.createFail({ message: error.message ?? error }))),
        ),
      ),
    ),
  );

  createInviteSuccess$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.createSuccess),
      map(() => NotificationsActions.success({ text: `Invitation to sent Successfully`, title: 'Invitation status' })),
    ),
  );

  createInviteFail$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.createFail),
      map(() => NotificationsActions.error({ text: `Failed to send invitation`, title: 'Invitation status' })),
    ),
  );

  selectInviteAfterEdit$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.createSuccess),
      filter(({ invites }) => invites.length > 0),
      map(({ invites }) => InviteActions.select({ id: invites[0].id })),
    ),
  );

  removeInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.remove),
      mergeMap(({ id }) =>
        this.service.delete(id).pipe(
          map(([invite]) => InviteActions.removeSuccess({ invite })),
          catchError((err) => of(InviteActions.removeFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  acceptInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.accept),
      mergeMap(({ id }) =>
        this.service.accept(id).pipe(
          map((invite) => InviteActions.acceptSuccess({ invite })),
          catchError((err) => of(InviteActions.acceptFail({ message: err.message ?? err }))),
        ),
      ),
    ),
  );

  acceptedInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.acceptSuccess),
      map(() => NotificationsActions.success({ text: `Invitation accepted`, title: 'Invitation Answer' })),
    ),
  );

  acceptedInviteFail$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.acceptFail),
      map(() => NotificationsActions.error({ text: `Failed to accept invitation`, title: 'Invitation Answer' })),
    ),
  );

  declineInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.decline),
      mergeMap(({ id }) =>
        this.service.decline(id).pipe(
          map((invite) => InviteActions.declineSuccess({ invite })),
          catchError((err) => of(InviteActions.declineFail(err || err?.message))),
        ),
      ),
    ),
  );

  declinedInvite$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.declineSuccess),
      withLatestFrom(this.store.pipe(select(ClusterManagementSelectors.clusters.clusterEntities))),
      map(() => NotificationsActions.success({ text: `Invitation declined`, title: 'Invitation Answer' })),
    ),
  );

  declinedInviteFail$ = createEffect(() =>
    this.actions.pipe(
      ofType(InviteActions.declineFail),
      map(() => NotificationsActions.error({ text: `Failed to decline invitation`, title: 'Invitation Answer' })),
    ),
  );

  constructor(
    private loader: LoaderService,
    private actions: Actions,
    private service: InvitesService,
    private store: Store<State>,
  ) {}
}
