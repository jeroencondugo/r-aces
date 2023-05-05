import * as fromSankeyData from './data.reducer';
import * as fromFilter from './filter.reducer';
import * as fromRoot from '@core/reducers';

export interface ArcSankeyState {
  data: fromSankeyData.State;
  filter: fromFilter.State;
}

export interface State extends fromRoot.State {
  arcSankey: ArcSankeyState;
}

export const reducers = {
  data: fromSankeyData.reducer,
  filter: fromFilter.reducer,
};
