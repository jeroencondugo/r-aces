import { decrementDateConfig, incrementDateConfig, startDateConfig } from '../../energy-insight/reducers/_config';
import { isPeriod, MeasureOption, TimePeriod } from '@shared/models/filters';
import { parseISO, startOfMonth } from 'date-fns';
import { FilterConfig, FilterConfigResponse, TimeRange } from '../models/filter-config.model';
import { Dict } from '@shared/utils/common.utils';
import { Id } from '@shared/models/id.model';
import { Action, createReducer, on } from '@ngrx/store';
import { clipDatePeriod, nowISO } from '@shared/utils/date.utils';
import { AuthActions } from '../../auth/actions';
import { Nullable } from '@shared/types/nullable.type';
import { ArcSankeyActions } from '../actions';

export interface State {
  configEntities: Dict<FilterConfig>;
  configIds: ReadonlyArray<Id>;
  configsLoaded: boolean;

  siteId: Nullable<Id>;
  startDate: string;
  endDate: string;
  selectedPeriod: TimePeriod;
  selectedMeasureOption: MeasureOption;
}

const initialState: State = {
  configEntities: {},
  configIds: [],
  configsLoaded: false,

  siteId: null,
  startDate: startOfMonth(new Date()).toISOString(),
  endDate: nowISO(),
  selectedPeriod: 'M',
  selectedMeasureOption: 'usage',
};

const filterReducer = createReducer(
  initialState,
  on(ArcSankeyActions.filter.loadConfigSuccess, (state, { ids: configIds, entities: configEntities }) => ({
    ...state,
    configEntities,
    configIds,
    configsLoaded: true,
  })),
  on(ArcSankeyActions.filter.selectSite, (state, { id: siteId }) => {
    const { extends: range, measureCategories } =
      state.configEntities[siteId] ?? <FilterConfigResponse>{ extends: {}, measureCategories: [], periods: [] };

    const getDefaultPeriod = () => {
      const availablePeriods = Object.keys(range).filter(isPeriod);
      const [defaultPeriod] = availablePeriods;
      return defaultPeriod ?? 'M';
    };
    const selectedPeriod = range[state.selectedPeriod] != null ? state.selectedPeriod : getDefaultPeriod();

    const selectedMeasureOption = measureCategories.includes(state.selectedMeasureOption)
      ? state.selectedMeasureOption
      : measureCategories[0] ?? 'usage';

    const { startDate, endDate = nowISO() } = range[selectedPeriod] ?? {
      startDate: null,
      endDate: null,
    };

    return {
      ...state,
      siteId,
      selectedPeriod,
      selectedMeasureOption,
      startDate: clipDatePeriod(state.startDate, { start: startDate, end: endDate, period: selectedPeriod }),
    };
  }),
  on(ArcSankeyActions.filter.selectPeriod, (state, { period }) => {
    const { extends: range } = state.configEntities[state.siteId] ?? { extends: <Dict<TimeRange, TimePeriod>>{} };

    const { startDate, endDate = nowISO() } = range[period] ?? {
      startDate: null,
      endDate: null,
    };

    return {
      ...state,
      selectedPeriod: period,
      startDate: clipDatePeriod(state.startDate, { start: startDate, end: endDate, period }),
    };
  }),
  on(ArcSankeyActions.filter.selectMeasure, (state, { measureOption }) => ({
    ...state,
    selectedMeasureOption: measureOption,
  })),
  on(ArcSankeyActions.filter.selectStartDate, (state, { date }) => {
    const period = state.selectedPeriod;
    const startDate = startDateConfig[period](parseISO(date)).toISOString();
    return {
      ...state,
      startDate,
    };
  }),
  on(ArcSankeyActions.filter.incrementDate, (state, { date }) => {
    const startDate = incrementDateConfig[state.selectedPeriod](parseISO(date)).toISOString();
    return {
      ...state,
      startDate,
    };
  }),
  on(ArcSankeyActions.filter.decrementDate, (state, { date }) => {
    const startDate = decrementDateConfig[state.selectedPeriod](parseISO(date)).toISOString();
    return {
      ...state,
      startDate,
    };
  }),
  on(AuthActions.domainChanged, () => initialState),
);

export function reducer(state: State, action: Action): State {
  return filterReducer(state, action);
}
