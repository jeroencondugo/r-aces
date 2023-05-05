import { createFeatureSelector, createSelector } from '@ngrx/store';
import { ClusterHeatmapState } from '../reducers';
import { getMeasure, getSelectedPeriod, getSelectedResolution, getStartDate } from './filter.selectors';
import { findColorScheme, generateSubtitle, getLabelFixer } from '../utils/chart.utils';
import { Color, HeatmapItem } from '@components/heatmap/heatmap.model';
import { PruneOut } from '@shared/types/prune-out.type';
import { HeatmapChart } from '../models/heatmap.model';

const getState = createFeatureSelector<ClusterHeatmapState>('clusterHeatmap');

const getDataState = createSelector(getState, ({ data }) => data);

export const getHeatmaps = createSelector(
  getDataState,
  getSelectedPeriod,
  getSelectedResolution,
  getMeasure,
  getStartDate,
  ({ heatmaps }, period, resolution, measure, startDate) => {
    const { unit } = measure ?? { unit: '' };
    const orderedHeatmaps = Object.keys(heatmaps)
      .map((id) => heatmaps[id])
      .sort(({ order: a }, { order: b }) => a - b);

    const fixLabel = getLabelFixer(period, resolution);

    return orderedHeatmaps.map(
      (heatmap) =>
        <HeatmapVM>{
          ...heatmap,
          colorScheme: findColorScheme(heatmap),
          subtitle: generateSubtitle(heatmap, orderedHeatmaps, measure, period, startDate),
          hideYAxisValues: heatmap.type === 'difference',
          data: {
            tiles: heatmap.data.map(fixLabel),
            unit,
          },
        },
    );
  },
);

export const getLoading = createSelector(getDataState, ({ loading }) => loading);

type HeatmapVM = PruneOut<HeatmapChart, 'data'> & {
  colorScheme: Color[];
  subtitle: string;
  hideYAxisValues: boolean;
  data: {
    tiles: HeatmapItem[];
    unit: string;
  };
};
