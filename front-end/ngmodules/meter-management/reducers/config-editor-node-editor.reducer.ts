import { Action, createReducer, on } from '@ngrx/store';
import { MeterMgmtActions } from '../actions';
import { Nullable } from '@shared/types/nullable.type';
import { Dict } from '@shared/utils/common.utils';
import { Id } from '@shared/models/id.model';

export interface State {
  outputMode: string;
  measure: Nullable<Id>;
  isConstantField: Dict<boolean, string>;
}

const initialState: State = {
  outputMode: 'diff',
  measure: null,
  isConstantField: {},
};

const actions = MeterMgmtActions.configEditorNodeDialog;

const configEditorReducer = createReducer(
  initialState,
  on(actions.selectOutputMode, (state, { outputMode }) => ({ ...state, outputMode })),
  on(actions.selectMeasure, (state, { measure }) => ({ ...state, measure })),
  on(actions.setIsConstant, (state, { field, isConstant }) => ({
    ...state,
    isConstantField: { ...state.isConstantField, [field]: isConstant },
  })),
);

export function reducer(state: State, action: Action): State {
  return configEditorReducer(state, action);
}
