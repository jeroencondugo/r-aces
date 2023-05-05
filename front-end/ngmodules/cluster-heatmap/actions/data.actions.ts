import { createAction, props } from '@ngrx/store';
import { HeatmapChart, HeatmapPayload } from '../models/heatmap.model';
import { FailPayload } from '@shared/models/fail-payload.model';
import { Dict } from '@shared/utils/common.utils';

const LABEL = '[Heatmap Data]';

export const data = {
  load: createAction(`${LABEL} Load data`, props<HeatmapPayload>()),
  loadSuccess: createAction(`${LABEL} Load data success`, props<{ heatmaps: Dict<HeatmapChart> }>()),
  loadFail: createAction(`${LABEL} Load data fail`, props<FailPayload>()),
  clear: createAction(`${LABEL} Clear data`)
};
