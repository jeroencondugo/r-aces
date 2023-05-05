import { Action, createReducer, on } from '@ngrx/store';
import { AuthActions } from '../../auth/actions';
import { Dict } from '@shared/utils/common.utils';
import { HeatmapChart } from '../models/heatmap.model';
import { HeatmapActions } from '../actions';

export interface State {
  heatmaps: Dict<HeatmapChart>;
  loading: boolean;
}

const initialState: State = {
  heatmaps: {},
  loading: false,
};

const dataReducer = createReducer(
  initialState,
  on(HeatmapActions.data.load, (state) => ({ ...state, heatmaps: {}, loading: true })),
  on(HeatmapActions.data.loadSuccess, (state, { heatmaps }) => ({ ...state, loading: false, heatmaps })),
  on(HeatmapActions.data.loadFail, (state) => ({ ...state, loading: false })),
  on(HeatmapActions.data.clear, AuthActions.domainChanged, () => initialState),
);

export function reducer(state: State, action: Action) {
  return dataReducer(state, action);
}
