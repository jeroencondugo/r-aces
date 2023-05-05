import { createAction, props } from '@ngrx/store';

import { Id } from '@shared/models/id.model';
import { InviteNormalized, InviteFormModel } from '../model/invite.model';
import { FailPayload } from '@shared/models/fail-payload.model';

export const load = createAction('[Cluster Management] Load invites');
export const loadSuccess = createAction(
  '[Cluster Management] Load invites success',
  props<{ invites: InviteNormalized[] }>(),
);
export const loadFail = createAction('[Cluster Management] Load invites fail', props<FailPayload>());

export const create = createAction('[Cluster Management] Create invite', props<{ invite: InviteFormModel }>());
export const createSuccess = createAction(
  '[Cluster Management] Create invite success',
  props<{ invites: InviteNormalized[] }>(),
);
export const createFail = createAction('[Cluster Management] Create invite fail', props<FailPayload>());

export const remove = createAction('[Cluster Management] Delete invite', props<{ id: Id }>());
export const removeSuccess = createAction(
  '[Cluster Management] Delete invite success',
  props<{ invite: InviteNormalized }>(),
);
export const removeFail = createAction('[Cluster Management] Delete invite fail', props<FailPayload>());

export const select = createAction('[Cluster Management] Select cluster invitation', props<{ id: Id }>());
export const selected = createAction('[Cluster Management] Cluster invitation selected', props<{ id: Id }>());

export const changePage = createAction('[Cluster Management] Invitation list page change', props<{ page: number }>());

export const accept = createAction('[Cluster Management] Cluster invite accept', props<{ id: Id }>());
export const acceptSuccess = createAction(
  '[Cluster Management] Cluster invite accepted',
  props<{ invite: InviteNormalized }>(),
);
export const acceptFail = createAction('[Cluster Management] Cluster invite accept fail', props<FailPayload>());

export const decline = createAction('[Cluster Management] Cluster invite decline', props<{ id: Id }>());
export const declineSuccess = createAction(
  '[Cluster Management] Cluster invite declined',
  props<{ invite: InviteNormalized }>(),
);
export const declineFail = createAction('[Cluster Management] Cluster invite decline fail', props<{ msg: string }>());
