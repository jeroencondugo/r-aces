import { createAction, props } from '@ngrx/store';
import { HeatmapConfig } from '../models/heatmap.model';
import { Id } from '@shared/models/id.model';
import { FailPayload } from '@shared/models/fail-payload.model';
import { TimePeriod, TimeResolution } from '@shared/models/filters';

const LABEL = '[Heatmap Filter]';
export const filter = {
  loadConfig: createAction(`${LABEL} Load config`, props<{ measure: Id }>()),
  loadConfigSuccess: createAction(`${LABEL} Load config success`, props<{ config: HeatmapConfig }>()),
  loadConfigFail: createAction(`${LABEL} Load config fail`, props<FailPayload>()),

  selectMeasure: createAction(`${LABEL} Select measure`, props<{ measure: Id }>()),
  selectPeriod: createAction(`${LABEL} Select period`, props<{ period: TimePeriod }>()),
  selectResolution: createAction(`${LABEL} Select resolution`, props<{ resolution: TimeResolution }>()),
  selectStartDate: createAction(`${LABEL} Select start date`, props<{ date: string }>()),
  incrementDate: createAction(`${LABEL} Increment start date`, props<{ date: string }>()),
  decrementDate: createAction(`${LABEL} Decrement start date`, props<{ date: string }>()),
};
