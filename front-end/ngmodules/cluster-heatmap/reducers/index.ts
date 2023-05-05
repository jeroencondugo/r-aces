import * as fromFilter from './filter.reducer';
import * as fromData from './data.reducer';
import * as fromMeters from './meters.reducer';

export interface ClusterHeatmapState {
  data: fromData.State;
  filter: fromFilter.State;
  meters: fromMeters.State;
}

export const reducers = {
  data: fromData.reducer,
  filter: fromFilter.reducer,
  meters: fromMeters.reducer,
};
