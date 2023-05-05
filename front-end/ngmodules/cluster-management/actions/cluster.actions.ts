import { createAction, props } from '@ngrx/store';

import { FailPayload } from '@shared/models/fail-payload.model';
import { Id } from '@shared/models/id.model';
import { ClusterNormalized, Cluster } from '../model/cluster.model';

export const load = createAction('[Cluster Management] Load clusters');
export const loadSuccess = createAction('[Cluster Management] Load clusters Success', props<{ clusters: ClusterNormalized[] }>());
export const loadFail = createAction('[Cluster Management] Load clusters Fail', props<{ error: FailPayload }>());

export const create = createAction('[Cluster Management] Create clusters', props<{ cluster: ClusterNormalized }>());
export const createSuccess = createAction(
  '[Cluster Management] Create clusters Success',
  props<{ cluster: ClusterNormalized }>(),
);
export const createFail = createAction('[Cluster Management] Create clusters Fail', props<{ err: FailPayload }>());

export const update = createAction(
  '[Cluster Management] Update clusters',
  props<{ cluster: Partial<ClusterNormalized> & { id: Id } }>(),
);
export const updateSuccess = createAction(
  '[Cluster Management] Update clusters Success',
  props<{ cluster: ClusterNormalized }>(),
);
export const updateFail = createAction('[Cluster Management] Update clusters Fail', props<{ err: FailPayload }>());

export const remove = createAction('[Cluster Management] Delete cluster', props<{ cluster: Cluster }>());
export const removeSuccess = createAction('[Cluster Management] Delete cluster Success', props<{ cluster: Id }>());
export const removeFail = createAction('[Cluster Management] Delete cluster Fail', props<{ err: FailPayload }>());

export const selectCluster = createAction('[Cluster Management] Select cluster', props<{ cluster: ClusterNormalized }>());
export const selected = createAction('[Cluster Management] Selected cluster', props<{ id: Id }>());

export const searchClusters = createAction(
  '[Cluster Management] Filter meters by search term',
  props<{ term: string }>(),
);

export const pageChange = createAction(
  '[Cluster Management] Cluster list page change',
  props<{ selectedPage: number }>(),
);

export const banClient = createAction(
  '[Cluster Management] Ban client',
  props<{ clients: Id[]; cluster: Id; reason: string }>(),
);
export const banClientSuccess = createAction('[Cluster Management] Ban client success', props<any>());
export const banClientFail = createAction('[Cluster Management] Ban client fail', props<{ err: FailPayload }>());
export const unbanClient = createAction('[Cluster Management] Unban client', props<{ clients: Id[]; cluster: Id }>());
export const unbanClientSuccess = createAction('[Cluster Management] Unban client success', props<any>());
export const unbanClientFail = createAction('[Cluster Management] Unban client fail', props<{ err: FailPayload }>());
