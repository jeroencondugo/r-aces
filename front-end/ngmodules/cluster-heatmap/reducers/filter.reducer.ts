import { Action, createReducer, on } from '@ngrx/store';
import { AuthActions } from '../../auth/actions';
import { Nullable } from '@shared/types/nullable.type';
import { Id } from '@shared/models/id.model';
import { HeatmapActions } from '../actions';
import { HeatmapConfig } from '../models/heatmap.model';
import { TimePeriod, TimeResolution } from '@shared/models/filters';
import { extractAvailablePeriods, extractAvailableResolutions } from '../utils/filter.utils';
import { clipDatePeriod, nowISO } from '@shared/utils/date.utils';
import { parseISO, startOfMonth } from 'date-fns';
import { decrementDateConfig, incrementDateConfig, startDateConfig } from '../../energy-insight/reducers/_config';
import { Dict } from '@shared/utils/common.utils';

export interface State {
  startDate: string;
  measure: Nullable<Id>;
  period: TimePeriod;
  resolution: TimeResolution;

  config: Nullable<HeatmapConfig>;
  configsPerMeasure: Dict<HeatmapConfig>;
  loading: boolean;
}

const initialState: State = {
  startDate: startOfMonth(new Date()).toISOString(),
  measure: null,
  period: 'W',
  resolution: 'H',

  config: null,
  configsPerMeasure: {},
  loading: false,
};

const filterReducer = createReducer(
  initialState,

  on(HeatmapActions.filter.loadConfig, (state) => ({ ...state, loading: true })),
  on(HeatmapActions.filter.loadConfigSuccess, (state, { config }) => {
    const availablePeriods = extractAvailablePeriods(config);
    const period = availablePeriods.includes(state.period) ? state.period : availablePeriods[0];
    const availableResolutions = extractAvailableResolutions(period, config);
    const resolution = availableResolutions.includes(state.resolution) ? state.resolution : availableResolutions[0];
    const { startDate, endDate = nowISO() } = config;

    return {
      ...state,
      loading: false,
      config,
      period,
      resolution,
      configsPerMeasure: { ...state.configsPerMeasure, [config.measure]: config },
      startDate: clipDatePeriod(state.startDate, { start: startDate, end: endDate, period }),
    };
  }),
  on(HeatmapActions.filter.loadConfigFail, (state) => ({ ...state, loading: false })),

  on(HeatmapActions.filter.selectMeasure, (state, { measure }) => ({ ...state, measure })),
  on(HeatmapActions.filter.selectPeriod, (state, { period }) => {
    const availableResolutions = extractAvailableResolutions(period, state.config);
    const resolution = availableResolutions.includes(state.resolution) ? state.resolution : availableResolutions[0];
    return { ...state, period, resolution };
  }),
  on(HeatmapActions.filter.selectResolution, (state, { resolution }) => ({ ...state, resolution })),
  on(HeatmapActions.filter.selectStartDate, (state, { date }) => {
    const period = state.period;
    const dateClipper = startDateConfig[period];
    if (dateClipper != null) {
      const startDate = dateClipper(parseISO(date)).toISOString();
      return {
        ...state,
        startDate,
      };
    }
    return state;
  }),
  on(HeatmapActions.filter.incrementDate, (state, { date }) => {
    const incrementer = incrementDateConfig[state.period];
    if (incrementer != null) {
      const startDate = incrementer(parseISO(date)).toISOString();
      return {
        ...state,
        startDate,
      };
    }
    return state;
  }),
  on(HeatmapActions.filter.decrementDate, (state, { date }) => {
    const decrementer = decrementDateConfig[state.period];
    if (decrementer != null) {
      const startDate = decrementer(parseISO(date)).toISOString();
      return {
        ...state,
        startDate,
      };
    }
    return state;
  }),
  on(AuthActions.domainChanged, () => initialState),
);

export function reducer(state: State, action: Action) {
  return filterReducer(state, action);
}
