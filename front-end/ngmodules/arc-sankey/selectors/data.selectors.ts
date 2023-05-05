import { createFeatureSelector, createSelector } from '@ngrx/store';
import { ArcSankeyState } from '../reducers';
import { createList } from '@shared/utils/selectors.utils';
import { Link } from '@components/arc-diagram/arc-diagram.model';
import { DataSelectors } from '@data/selectors';
import { CommodityType } from '@shared/models/commodity-type.model';
import { Dict, roundToDigits, sameIds, toArray } from '@shared/utils/common.utils';
import { GraphLinkNormalized } from '../models/graph-link.model';
import { MeasureOption } from '@shared/models/filters';
import { getSelectedMeasureOption } from './filter.selectors';
import { SettingsSelectors } from '../../settings/selectors';
import { GraphNode } from '../models/graph-node.model';

export const getState = createFeatureSelector<ArcSankeyState>('arc-sankey');

const getDataState = createSelector(getState, ({ data }) => data);

const getNodesEntities = createSelector(getDataState, ({ nodeEntities }) => nodeEntities);
const getLinkEntities = createSelector(getDataState, ({ linkEntities }) => linkEntities);
const getLinksIds = createSelector(getDataState, ({ linkIds }) => linkIds);

const getLinks = createSelector(getLinksIds, getLinkEntities, createList);

export const getLoading = createSelector(getDataState, ({ loading }) => loading);
export const getLoaded = createSelector(getDataState, ({ loaded }) => loaded);

export const getData = createSelector(
  getNodesEntities,
  getLinks,
  DataSelectors.commodityTypes.getEntities,
  getSelectedMeasureOption,
  SettingsSelectors.getThemeColors,
  (nodeEntities, normalizedLinks, commodityTypes, measureOption, { foreground, primary }) => {
    const links = (normalizedLinks ?? []).map(linkDenormalizer(commodityTypes, measureOption, foreground));
    return <{ nodes: GraphNode[]; links: Link[] }>{
      links,
      nodes: toArray(nodeEntities).map((node) => ({
        ...node,
        color: primary,
        input: links
          .filter(({ target }) => sameIds(target, node.id))
          .reduce((aggregate, { value }) => aggregate + value, 0),
        output: links
          .filter(({ source }) => sameIds(source, node.id))
          .reduce((aggregate, { value }) => aggregate + value, 0),
        inputUnit: links.find(({ target }) => sameIds(target, node.id))?.unit,
        outputUnit: links.find(({ source }) => sameIds(source, node.id))?.unit,
      })),
    };
  },
);

const DIGITS = [
  { value: 1, digits: 3 },
  { value: 10, digits: 2 },
  { value: 100, digits: 1 },
  { value: 1000, digits: 0 },
];
export function linkDenormalizer(commodityTypes: Dict<CommodityType>, measureOption: MeasureOption, linkColor: string) {
  return (link: GraphLinkNormalized) => {
    const roundedValue = roundLinkValue(link[measureOption]?.value);
    return {
      ...link,
      color: commodityTypes[link.commodityType]?.color ?? linkColor,
      value: roundedValue,
      label: roundedValue != null ? `${roundedValue}${' ' + link[measureOption]?.unit}` : 'N/A',
      commodityType: commodityTypes[link.commodityType],
      unit: link[measureOption]?.unit,
    };
  };
}

function roundLinkValue(value: number): number {
  const numberOfDigits = DIGITS.find((digits) => digits.value >= Math.abs(value ?? 0))?.digits ?? 0;
  const roundedValue = value != null ? roundToDigits(value, numberOfDigits) : value;
  return roundedValue;
}

export const hasData = createSelector(getData, (data) => data.nodes.length > 0);
