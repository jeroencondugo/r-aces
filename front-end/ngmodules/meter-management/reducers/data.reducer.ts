import { Action, createReducer, on } from '@ngrx/store';

import { Dict } from '@shared/utils/common.utils';
import { MeterMgmtActions } from '../actions';
import { MeterConfigMeta } from '../models/data.model';

export interface State {
  configTypes: Dict<MeterConfigMeta>;
  configTypeIds: ReadonlyArray<string>;
}

const initialState: State = {
  configTypes: {},
  configTypeIds: [],
};

const dataActions = MeterMgmtActions.data;

const dataReducer = createReducer(
  initialState,
  on(dataActions.loadMeterConfigsCatalogSuccess, (state, { catalog }) => {
    const data = catalog || [];
    const configTypes = data.reduce(
      (entities, cur) => ({
        ...entities,
        [cur.type]: cur,
      }),
      <Dict<MeterConfigMeta>>{},
    );

    const configTypeIds = data.map(({ type }) => type);
    return {
      ...state,
      configTypes,
      configTypeIds,
    };
  }),
);

export function reducer(state: State, action: Action): State {
  return dataReducer(state, action);
}
