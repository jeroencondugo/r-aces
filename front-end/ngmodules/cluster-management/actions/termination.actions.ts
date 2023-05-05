import { createAction, props } from '@ngrx/store';

import { Id } from '@shared/models/id.model';
import { TerminationNormalized, TerminationForm } from '../model/termination.model';
import { FailPayload } from '@shared/models/fail-payload.model';

export const load = createAction('[Cluster Management] Load terminations');
export const loadSuccess = createAction(
  '[Cluster Management] Load terminations success',
  props<{ terminations: TerminationNormalized[] }>(),
);
export const loadFail = createAction('[Cluster Management] Load terminations fail', props<FailPayload>());

export const create = createAction(
  '[Cluster Management] Create termination',
  props<{ termination: TerminationForm }>(),
);
export const createSuccess = createAction(
  '[Cluster Management] Create termination success',
  props<{ terminations: TerminationNormalized[] }>(),
);
export const createFail = createAction('[Cluster Management] Create termination fail', props<FailPayload>());

export const remove = createAction('[Cluster Management] Delete termination', props<{ id: Id }>());
export const removeSuccess = createAction(
  '[Cluster Management] Delete termination success',
  props<{ termination: TerminationNormalized }>(),
);
export const removeFail = createAction('[Cluster Management] Delete termination fail', props<FailPayload>());

export const select = createAction('[Cluster Management] Select cluster termination', props<{ id: Id }>());
export const selected = createAction('[Cluster Management] Cluster termination selected', props<{ id: Id }>());

export const changePage = createAction('[Cluster Management] Termination list page change', props<{ page: number }>());

export const accept = createAction('[Cluster Management] Cluster terminate accept', props<{ id: Id }>());
export const acceptSuccess = createAction(
  '[Cluster Management] Cluster termination accepted',
  props<{ termination: TerminationNormalized }>(),
);
export const acceptFail = createAction('[Cluster Management] Cluster terminate accept fail', props<FailPayload>());

export const decline = createAction('[Cluster Management] Cluster terminate decline', props<{ id: Id }>());
export const declineSuccess = createAction(
  '[Cluster Management] Cluster termination declined',
  props<{ termination: TerminationNormalized }>(),
);
export const declineFail = createAction(
  '[Cluster Management] Cluster termination decline fail',
  props<{ msg: string }>(),
);
