import { ClusterHeatmapType, HeatmapChart } from '../models/heatmap.model';
import { Dict, percentileFormatter, roundToDigits } from '@shared/utils/common.utils';
import { ColorRange, HeatmapItem } from '@components/heatmap/heatmap.model';
import { TimePeriod, TimeResolution } from '@shared/models/filters';
import { format, parseISO } from 'date-fns';
import { Measure } from '@shared/models/measure.model';
import { datetimeSettingsConfig } from '../../energy-insight/reducers/_config';
import { capitalize } from '@pipes/capital-case.pipe';
import { calculateColorScheme } from '@components/heatmap/utils/color-scheme.utils';
const COLOR_RANGE: Dict<ColorRange, ClusterHeatmapType> = {
  demand: { from: '#e9f2cd', to: '#8eb92e' },
  excess: { from: '#ffcdd2', to: '#b71c1c' },
  difference: { from: '#c2c9dd', to: '#2d4386' },
  overlap: { from: '#c2c9dd', to: '#2d4386' },
};

export function findColorScheme(heatmap: HeatmapChart) {
  const extent = calculateExtent(heatmap);

  const negativeColorScheme =
    extent.negative != null
      ? calculateColorScheme({
          colorRange: { from: '#b71c1c', to: '#ffcdd2' },
          extent: extent.negative,
          colorCount: 5,
        })
      : [];

  const positiveColorScheme =
    extent.positive != null
      ? calculateColorScheme({
          colorRange: COLOR_RANGE[heatmap.type] ?? { from: '#c2c9dd', to: '#2d4386' },
          extent: extent.positive,
          colorCount: 5,
        })
      : [];

  return [...negativeColorScheme, ...positiveColorScheme];
}

export function generateSubtitle(
  heatmap: HeatmapChart,
  allHeatmaps: readonly HeatmapChart[],
  measure: Measure,
  period: TimePeriod,
  date: Date,
) {
  const dateString = format(date, datetimeSettingsConfig[period].format);
  if (heatmap.type === 'excess' || heatmap.type === 'demand') {
    return `Total ${measure.category} ${heatmap.type}  for ${dateString} is ${roundToDigits(
      findTotalValue(heatmap),
      1,
    )} ${measure.unit}`;
  }
  if (heatmap.type === 'overlap') {
    const totalDemand = findTotalValue(allHeatmaps.find(({ type }) => type === 'demand'));
    const totalExcess = findTotalValue(allHeatmaps.find(({ type }) => type === 'excess'));
    const totalOverlap = findTotalValue(heatmap);
    const excessPercentage = percentileFormatter(totalOverlap / totalExcess);
    const demandPercentage = percentileFormatter(totalOverlap / totalDemand);
    return `Total ${measure.category} overlap for ${dateString} is ${roundToDigits(totalOverlap)} ${
      measure.unit
    } (${excessPercentage} of excess, ${demandPercentage} of demand)`;
  }
  if (heatmap.type === 'difference') {
    return `${capitalize(measure.category)} differences for ${dateString}`;
  }
  return null;
}

function findTotalValue({ data }: HeatmapChart) {
  return data.reduce((total, [, , value]) => total + value, 0);
}

export function getLabelFixer(period: TimePeriod, resolution: TimeResolution) {
  return ([y, x, value]: HeatmapItem) => {
    const xLabel = fixXLabel(x, resolution);
    const yLabel = fixYLabel(y, period);
    return <HeatmapItem>[yLabel, xLabel, value];
  };
}

const resolutionParsers: Dict<(date: string) => string, TimeResolution> = {
  D: (date: string) => `${format(parseISO(date), 'iiii')}`,
  H: (date: string) => `${format(parseISO(date), 'H:mm')}`,
  M: (date: string) => `${format(parseISO(date), 'MMM')}`,
  Q: (date: string) => `${format(parseISO(date), 'QQQ')}`,
  QH: (date: string) => `${format(parseISO(date), 'H:mm')}`,
  W: (date: string) => `${format(parseISO(date), 'I')} w`,
  Y: (date: string) => `${format(parseISO(date), 'y')}`,
};

const periodParsers: Dict<(date: string) => string, TimePeriod> = {
  D: (date) => date,
  M: (date) => `${format(parseISO(date), 'PP')}`,
  Q: (date) => `${format(parseISO(date), 'MMM')}`,
  W: (date) => `${format(parseISO(date), 'cccc')}`,
  Y: (date) => `${format(parseISO(date), 'MMM')}`,
  All: (date) => date,
};
function fixXLabel(isoDate: string, resolution: TimeResolution) {
  return resolutionParsers[resolution](isoDate);
}

function fixYLabel(isoDate: string, period: TimePeriod) {
  return periodParsers[period](isoDate);
}

function calculateExtent(heatmap: HeatmapChart) {
  const values = heatmap.data.map(([, , value]) => value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);

  const negative = { min: Math.min(0, minValue), max: 0 };
  const positive = { min: 0, max: Math.max(0, maxValue) };

  return {
    ...(minValue < 0 && { negative }),
    ...(maxValue >= 0 && { positive }),
  };
}
