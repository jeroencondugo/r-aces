import { createFeatureSelector, createSelector } from '@ngrx/store';
import * as fromRoot from '@core/reducers';
import * as fromData from './data.reducer';
import * as fromConfigEditor from './config-editor.reducer';
import * as fromConfigEditorNodeDialog from './config-editor-node-editor.reducer';
import * as fromMetersList from './meters-list.reducer';
import { Meter } from '@shared/models';
import { Dict } from '@shared/utils/common.utils';

import {
  InputPortNormalized,
  MeterConfig,
  MeterConfigNormalized,
  OutputPortNormalized,
} from '../models/meter-config.model';
import { LayoutEdge } from '../../graph/model/graph.model';
import { DataSelectors } from '@data/selectors';
import { orderBy } from '@shared/utils/array.utils';
import { ConfigEditorSelectors, DataSelectors as MeterMgmtDataSelectors, MetersListSelectors } from '../selectors';
import { Changes, MeterConfigChangeset } from '../models/changeset.model';
import { GraphChangeType } from '../../structure-management/models/graph-changeset';
import { connectionResolver, createVirtualMeter, denormalizeMeter } from '../utils/meters.utils';
import { getConnectedPortId } from '../selectors/config-editor.selectors';
import { isCommodityTypeBasetree, isSiteBasetree } from '../../structure-management/models/basetree';

export interface MeterManagementState {
  data: fromData.State;
  configEditor: fromConfigEditor.State;
  configEditorNodeDialog: fromConfigEditorNodeDialog.State;
  metersList: fromMetersList.State;
}

export interface State extends fromRoot.State {
  'meter-management': MeterManagementState;
}

export const reducers = {
  data: fromData.reducer,
  configEditor: fromConfigEditor.reducer,
  configEditorNodeDialog: fromConfigEditorNodeDialog.reducer,
  metersList: fromMetersList.reducer,
};

/**
 * Selectors
 */
export const getMeterManagementState = createFeatureSelector<MeterManagementState>('meter-management');

const sortOptions: Dict<(meter: Meter) => string> = {
  name: (meter) => meter.name,
  commodityType: (meter) => meter.commodityType?.name ?? '',
  meterType: (meter) => meter.meterType?.name ?? '',
  site: (meter) => meter.site?.name ?? '',
};
const getMetersCollection = createSelector(
  DataSelectors.meters.getMetersDenormalized,
  MetersListSelectors.getSortingArray,
  (meters, sorting) => {
    if (sorting.length <= 0) {
      return meters;
    }

    const sortedMeters = <Meter[]>orderBy(
      meters,
      sorting.map((sort) => sortOptions[sort.key]),
      sorting.map((sort) => <'asc' | 'desc' | null>sort.order),
    );

    return sortedMeters || [];
  },
);

export const getMetersFilteredCollection = createSelector(
  getMetersCollection,
  MetersListSelectors.getSearchTerm,
  (meterArray, searchTerm) => meterArray.filter((meter) => validateSearchTerm(meter, searchTerm)),
);

export const getSelectedMeterNormalized = createSelector(
  DataSelectors.meters.getEntities,
  MetersListSelectors.getSelectedId,
  (entities, id) => entities[id],
);

export const getSelectedMeter = createSelector(
  getSelectedMeterNormalized,
  DataSelectors.measures.getEntities,
  DataSelectors.meterTypes.getEntities,
  DataSelectors.commodityTypes.getEntities,
  DataSelectors.sites.getEntities,
  DataSelectors.basetrees.getList,
  (meter, measures, types, commodityTypes, sites, basetrees) => {
    const commodityTypeResolver = connectionResolver(basetrees, isCommodityTypeBasetree, commodityTypes);
    const siteResolver = connectionResolver(basetrees, isSiteBasetree, sites);
    return denormalizeMeter(meter, measures, types, commodityTypeResolver, siteResolver);
  },
);

export const getSelectedPageClamp = createSelector(
  MetersListSelectors.getSelectedPage,
  MetersListSelectors.getPageSize,
  getMetersFilteredCollection,
  (page, pageSize, meters) => {
    const length = meters ? meters.length : 0;
    const pagesCount = Math.ceil(length / pageSize);
    return page < pagesCount ? page : pagesCount - 1;
  },
);

export const getVisibleMeters = createSelector(
  getMetersFilteredCollection,
  getSelectedPageClamp,
  MetersListSelectors.getPageSize,
  (metersCollection, selectedPage, pageSize) => {
    const offset = pageSize * selectedPage;
    return metersCollection.slice(offset, offset + pageSize);
  },
);

export const getMeterConfigsData = createSelector(
  ConfigEditorSelectors.getEntities,
  getSelectedMeter,
  getConnectedPortId,
  (entities, selectedMeter, connectedPort) => {
    if (!selectedMeter) {
      return { nodes: {}, outputPorts: {}, inputPorts: {} };
    }
    const { nodes, inputPorts, outputPorts } = entities;
    const { inputPort, meter } = createVirtualMeter(selectedMeter, outputPorts[connectedPort]);
    return {
      nodes: { ...nodes, [meter.id]: meter },
      inputPorts: { ...inputPorts, [inputPort.id]: inputPort },
      outputPorts,
    };
  },
);

export const getGraphWithChanges = createSelector(
  getMeterConfigsData,
  ConfigEditorSelectors.getChangesetEntities,
  ConfigEditorSelectors.getChangesetIds,
  (data, changesets, changesetsIds) =>
    applyChanges(data.nodes, data.inputPorts, data.outputPorts, changesets, changesetsIds),
);

export const getMeterConfigsGraphLayout = createSelector(
  getGraphWithChanges,
  MeterMgmtDataSelectors.getConfigTypesEntities,
  (currentGraph, metadata) => {
    const { nodes: configs, inputPorts, outputPorts } = currentGraph;
    const nodes: MeterConfig[] = Object.keys(configs).map((id) => ({
      ...configs[id],
      inputPorts: configs[id].inputPorts.map((_id) => inputPorts[_id]),
      outputPorts: configs[id].outputPorts.map((_id) => outputPorts[_id]),
      metadata: metadata[configs[id].catalogId],
      label: getLabel(configs[id].name),
    }));

    const _inputPorts = nodes.reduce((agg, node) => [...agg, ...node.inputPorts], <InputPortNormalized[]>[]);

    const edges: LayoutEdge[] = _inputPorts
      .filter(({ outputNodeId }) => outputNodeId != null && configs[outputNodeId] != null)
      .map(({ outputNodeId, graphNodeId }) => ({ inputNode: graphNodeId, outputNode: outputNodeId }));

    return { nodes, edges };
  },
);

function getLabel(name: string) {
  if (!name || name.length <= 10) {
    return name;
  }
  const totalChars = 10;
  const fillChars = '..';
  const startChars = 3;
  const endChars = totalChars - startChars - fillChars.length;
  return `${name.slice(0, startChars)}${fillChars}${name.slice(name.length - endChars, name.length)}`;
}

function validateSearchTerm(meter: Meter, searchTerm: string) {
  const lowercasedSearchTerm = searchTerm.toLowerCase();
  return lowercasedSearchTerm.length > 1
    ? meter.name.toLowerCase().includes(lowercasedSearchTerm) ||
        (meter.meterType != null && meter.meterType.name.toLowerCase().includes(lowercasedSearchTerm)) ||
        (meter.site != null && meter.site.name.toLowerCase().includes(lowercasedSearchTerm)) ||
        (meter.commodityType != null && meter.commodityType.name.toLowerCase().includes(lowercasedSearchTerm))
    : true;
}

function applyChanges(
  nodeEntities: Dict<MeterConfigNormalized>,
  inputPortEntities: Dict<InputPortNormalized>,
  outputPortEntities: Dict<OutputPortNormalized>,
  changesetEntities: Dict<MeterConfigChangeset>,
  changesetIds: ReadonlyArray<number>,
): Changes {
  const sortedChanges = ([...changesetIds].sort((a, b) => a - b) || []).map((id) => changesetEntities[id]);
  const initialLayout = {
    nodes: nodeEntities,
    inputPorts: inputPortEntities,
    outputPorts: outputPortEntities,
  };
  return sortedChanges.reduce((changes: Changes, currentChange: MeterConfigChangeset) => {
    switch (currentChange.type) {
      case GraphChangeType.NodeAdded: {
        const nodes: Dict<MeterConfigNormalized> = {
          ...changes.nodes,
          [currentChange.node.id]: {
            ...(<any>currentChange.node),
            inputPorts: currentChange.node.inputPorts.map((p) => p.id),
            outputPorts: currentChange.node.outputPorts.map((p) => p.id),
          },
        };
        const inputPorts = {
          ...changes.inputPorts,
          ...currentChange.node.inputPorts.reduce(
            (inPorts, port) => ({ ...inPorts, [port.id]: port }),
            <Dict<InputPortNormalized>>{},
          ),
        };
        const outputPorts = {
          ...changes.outputPorts,
          ...currentChange.node.outputPorts.reduce(
            (outPorts, port) => ({ ...outPorts, [port.id]: port }),
            <Dict<OutputPortNormalized>>{},
          ),
        };
        return {
          nodes,
          inputPorts,
          outputPorts,
        };
      }

      case GraphChangeType.NodeDeleted: {
        const deletedId = currentChange.node.id;
        const { [deletedId]: deletedNode, ...nodes } = changes.nodes;

        const outPortIds = Object.keys(changes.outputPorts) || [];
        const outputPorts = outPortIds
          .filter((id) => !deletedNode.outputPorts.includes(id))
          .map((id) => changes.outputPorts[id])
          .reduce(
            (outPorts, currentPort) => ({
              ...outPorts,
              [currentPort.id]: currentPort,
            }),
            <Dict<OutputPortNormalized>>{},
          );

        const inPortIds = Object.keys(changes.inputPorts) || [];
        const inputPorts = inPortIds
          .filter((id) => !deletedNode.inputPorts.includes(id))
          .map((id) => changes.inputPorts[id])
          .reduce(
            (inPorts, currentPort) => ({
              ...inPorts,
              [currentPort.id]: {
                ...currentPort,
                outputPortId: !deletedNode.outputPorts.includes(currentPort.outputPortId)
                  ? currentPort.outputPortId
                  : null,
                outputNodeId: !deletedNode.outputPorts.includes(currentPort.outputPortId)
                  ? currentPort.outputNodeId
                  : null,
              },
            }),
            <Dict<InputPortNormalized>>{},
          );

        return {
          nodes,
          outputPorts,
          inputPorts,
        };
      }
      case GraphChangeType.NodeModified: {
        if (currentChange.node.inputPorts == null) {
          return {
            ...changes,
            nodes: {
              ...changes.nodes,
              [currentChange.node.id]: {
                ...changes.nodes[currentChange.node.id],
                ...(<any>currentChange.node),
              },
            },
          };
        } else {
          const nodes: Dict<MeterConfigNormalized> = {
            ...changes.nodes,

            [currentChange.node.id]: {
              ...changes.nodes[currentChange.node.id],
              ...(<any>currentChange.node),
              inputPorts: currentChange.node.inputPorts.map((p) => p.id),
              outputPorts: currentChange.node.outputPorts.map((p) => p.id),
            },
          };
          const inputPorts = {
            ...changes.inputPorts,
            ...currentChange.node.inputPorts.reduce(
              (inPorts, port) => ({ ...inPorts, [port.id]: port }),
              <Dict<InputPortNormalized>>{},
            ),
          };

          return {
            nodes,
            inputPorts,
            outputPorts: changes.outputPorts,
          };
        }
      }

      case GraphChangeType.InputPortModified: {
        const {
          port: { id: portId, outputPortId, outputNodeId },
        } = currentChange;
        const inPort = changes.inputPorts[portId];

        return {
          ...changes,
          inputPorts: {
            ...changes.inputPorts,
            [portId]: {
              ...inPort,
              outputPortId,
              outputNodeId,
            },
          },
        };
      }
    }

    return changes;
  }, initialLayout);
}
