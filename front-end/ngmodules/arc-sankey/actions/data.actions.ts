import { createAction, props } from '@ngrx/store';
import { TimePeriod } from '@shared/models/filters';

import { GraphNodeNormalized } from '../models/graph-node.model';
import { GraphLinkNormalized } from '../models/graph-link.model';

import { Id } from '@shared/models/id.model';

const LABEL = '[Arc sankey Data]';

export const load = createAction(
  `${LABEL} Load sankey data for site id`,
  props<{ siteId: Id; startDate: string; period: TimePeriod }>(),
);

export const loadFail = createAction(`${LABEL} Load sankey data failed`, props<{ message: string }>());
export const loadSuccess = createAction(
  `${LABEL} Load sankey data success`,
  props<{ nodes: GraphNodeNormalized[]; links: GraphLinkNormalized[] }>(),
);
export const clear = createAction(`${LABEL} Clear data`);
