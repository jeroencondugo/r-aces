import { createAction, props } from '@ngrx/store';
import { Id } from '@shared/models/id.model';

const LABEL = '[Heatmap Meters]';
export const meters = {
  selectExcess: createAction(`${LABEL} Select excess`, props<{ selection: readonly Id[] }>()),
  selectDemand: createAction(`${LABEL} Select demand`, props<{ selection: readonly Id[] }>()),
};
