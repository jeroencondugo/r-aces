import { Action, createReducer, on } from '@ngrx/store';
import { AuthActions } from '../../auth/actions';
import { Id } from '@shared/models/id.model';
import { HeatmapActions } from '../actions';

export interface State {
  excessMeters: readonly Id[];
  demandMeters: readonly Id[];
}

const initialState: State = {
  excessMeters: [],
  demandMeters: [],
};

const metersReducer = createReducer(
  initialState,
  on(HeatmapActions.meters.selectDemand, (state, { selection }) => ({ ...state, demandMeters: selection })),
  on(HeatmapActions.meters.selectExcess, (state, { selection }) => ({ ...state, excessMeters: selection })),
  on(HeatmapActions.filter.selectMeasure, (state) => ({ ...state, demandMeters: [], excessMeters: [] })),
  on(AuthActions.domainChanged, () => initialState),
);

export function reducer(state: State, action: Action) {
  return metersReducer(state, action);
}
