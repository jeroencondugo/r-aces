import { createAction, props } from '@ngrx/store';
import { MeasureOption, TimePeriod } from '@shared/models/filters';
import { Id } from '@shared/models/id.model';
import { Dict } from '@shared/utils/common.utils';
import { FilterConfig } from '../models/filter-config.model';

const LABEL = '[Arc sankey filter]';

export const decrementDate = createAction(`${LABEL} Decrement start date`, props<{ date: string }>());
export const incrementDate = createAction(`${LABEL} Increment start date`, props<{ date: string }>());
export const loadConfig = createAction(`${LABEL} Load config`);
export const loadConfigFail = createAction(`${LABEL} Load config fail`, props<{ message: string }>());
export const loadConfigSuccess = createAction(
  `${LABEL} Load config success`,
  props<{ ids: ReadonlyArray<Id>; entities: Dict<FilterConfig> }>(),
);
export const selectPeriod = createAction(`${LABEL} Select viewed period`, props<{ period: TimePeriod }>());
export const selectSite = createAction(`${LABEL} Select site id`, props<{ id: Id }>());
export const selectStartDate = createAction(`${LABEL} Select start date`, props<{ date: string }>());
export const siteIdFromCache = createAction(`${LABEL} Site Id From Cache`, props<{ id: string }>());
export const selectMeasure = createAction(`${LABEL} Select measure option`, props<{ measureOption: MeasureOption }>());
