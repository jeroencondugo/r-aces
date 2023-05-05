import { Dict, omitKeys, omitKeysBy, sameIds, toArray, toDict } from '@shared/utils/common.utils';
import { InputPortNormalized, MeterConfig, MeterConfigNormalized, OutputPortNormalized } from '../models/meter-config.model';
import { Id } from '@shared/models/id.model';
import { ChangesDTO, ConfigUpdate, MeterConfigChangeset } from '../models/changeset.model';
import { GraphChangeType } from '../../structure-management/models/graph-changeset';
import { Nullable } from '@shared/types/nullable.type';

interface SquashedChanges {
  meterId: string | number;
  addedNodes: Dict<MeterConfig>;
  deletedNodes: ReadonlyArray<Id>;
  modifiedInputPorts: Dict<InputPortNormalized>;
  modifiedNodes: Dict<MeterConfigNormalized>;
  connectedPort: Nullable<Id>;
}

export function squashChanges(
  changeList: Dict<any>,
  meterId: Id,
  originalEntities: {
    nodes: Dict<MeterConfigNormalized>;
    inputPorts: Dict<InputPortNormalized>;
    outputPorts: Dict<OutputPortNormalized>;
  },
  connectedPort: Nullable<Id>,
): SquashedChanges {
  const squashedChanges = <SquashedChanges>toArray<MeterConfigChangeset>(changeList).reduce(
    (finalChanges, change) => {
      switch (change.type) {
        case GraphChangeType.NodeAdded: {
          const { node } = change;
          return {
            ...finalChanges,
            addedNodes: {
              ...finalChanges.addedNodes,
              [node.id]: node,
            },
          };
        }

        case GraphChangeType.NodeModified: {
          const nodeAdded = finalChanges.addedNodes[change.node.id];
          return nodeAdded != null
            ? {
                ...finalChanges,
                addedNodes: {
                  ...finalChanges.addedNodes,
                  [change.node.id]: { ...nodeAdded, ...change.node },
                },
              }
            : {
                ...finalChanges,
                modifiedNodes: {
                  ...finalChanges.modifiedNodes,
                  [change.node.id]: {
                    ...finalChanges.modifiedNodes[change.node.id],
                    ...change.node,
                  },
                },
              };
        }

        case GraphChangeType.NodeDeleted: {
          const {
            node: { id: deletedNodeId },
          } = change;
          const update =
            finalChanges.addedNodes[deletedNodeId] != null
              ? { addedNodes: omitKeys(finalChanges.addedNodes, [deletedNodeId]) }
              : { deletedNodes: [...finalChanges.deletedNodes.filter((id) => id !== deletedNodeId), deletedNodeId] };

          const cleanModifiedInputPorts = omitKeysBy(finalChanges.modifiedInputPorts, (inputPort) =>
            sameIds(inputPort.graphNodeId, deletedNodeId),
          );
          const detachedInputPortsUpdate = detachConnectedPorts(deletedNodeId, originalEntities, finalChanges);

          return {
            ...finalChanges,
            ...update,
            modifiedNodes: omitKeys(finalChanges.modifiedNodes, [deletedNodeId]),
            modifiedInputPorts: omitKeysBy(
              {
                ...cleanModifiedInputPorts,
                ...detachedInputPortsUpdate,
              },
              (port) => typeof port.id === 'string' && port.id.includes('meter_'),
            ),
          };
        }

        case GraphChangeType.InputPortModified: {
          const { port: updatedPort } = change;

          return {
            ...finalChanges,
            modifiedInputPorts: {
              ...finalChanges.modifiedInputPorts,
              [updatedPort.id]: {
                ...finalChanges.modifiedInputPorts[updatedPort.id],
                ...updatedPort,
              },
            },
          };
        }

        default: {
          console.warn(`Config editor squashChanges: Change doesn't have valid handler`, change);
          return finalChanges;
        }
      }
    },
    <SquashedChanges>{
      meterId,
      addedNodes: {},
      deletedNodes: [],
      modifiedInputPorts: {},
      modifiedNodes: {},
      connectedPort,
    },
  );

  return squashedChanges;
}

export function serializeChanges({
  meterId: id,
  deletedNodes: remove,
  addedNodes,
  modifiedInputPorts,
  modifiedNodes,
  connectedPort,
}: SquashedChanges): ChangesDTO {
  const create = toArray(addedNodes).map((node) => ({
    ...node,
    inputPorts: (node.inputPorts || []).map((port) => ({ ...port, ...modifiedInputPorts[port.id] })),
  }));

  const update = toArray(omitKeysBy(modifiedInputPorts, (port) => addedNodes[port.graphNodeId] != null)).reduce(
    (nodes, port) => {
      const { inputPorts = [] } = nodes[port.graphNodeId] || { inputPorts: <readonly InputPortNormalized[]>[] };
      return {
        ...nodes,
        [port.graphNodeId]: {
          ...nodes[port.graphNodeId],
          id: port.graphNodeId,
          inputPorts: [...inputPorts.filter((_port) => !sameIds(_port.id, port.id)), port],
        },
      };
    },
    <Dict<ConfigUpdate>>toDict(toArray(modifiedNodes).map((node) => ({ ...node, inputPorts: [] }))),
  );

  return {
    id,
    connectedPort,
    configs: {
      update: toArray(update),
      create,
      remove,
    },
  };
}

// TODO: This function can and should be simplified
function detachConnectedPorts(
  deletedNodeId: Id,
  originalEntities: {
    nodes: Dict<MeterConfigNormalized>;
    inputPorts: Dict<InputPortNormalized>;
  },
  currentChanges: SquashedChanges,
): Dict<InputPortNormalized> {
  const { nodes, inputPorts } = originalEntities;
  const { modifiedInputPorts, addedNodes, deletedNodes } = currentChanges;
  const deletedNodeIds = [...deletedNodes, deletedNodeId];

  const originalInputPorts = toArray(nodes, { excludeIds: deletedNodeIds }).reduce(
    (portsPerNode, currentNode) => ({
      ...portsPerNode,
      // TODO: try simplifying by filtering here instead of omitting later
      [currentNode.id]: currentNode.inputPorts.map((id) => inputPorts[id]),
    }),
    <Dict<InputPortNormalized[]>>{},
  );

  const addedInputPorts = toArray(addedNodes, { excludeIds: deletedNodeIds }).reduce(
    (portsPerNode, currentNode) => ({
      ...portsPerNode,
      [currentNode.id]: currentNode.inputPorts.map((port) => ({ ...port, ...modifiedInputPorts[port.id] })),
    }),
    <Dict<InputPortNormalized[]>>{},
  );

  const affectedAddedAndOriginalInputPorts = toArray({
    ...originalInputPorts,
    ...addedInputPorts,
  }).reduce(
    (inputPortEntities, ports) => ({
      ...inputPortEntities,
      ...toDict(ports, {
        exclude: (inPort) =>
          inPort.graphNodeId === deletedNodeId || inPort.outputNodeId == null || inPort.outputNodeId !== deletedNodeId,
      }),
    }),
    <Dict<InputPortNormalized>>{},
  );

  const cleanModifiedInputPorts = omitKeysBy(
    modifiedInputPorts,
    (port) =>
      deletedNodeIds.includes(port.graphNodeId) || port.outputNodeId == null || port.outputNodeId !== deletedNodeId,
  );

  const inputPortsToDisconnect = {
    ...affectedAddedAndOriginalInputPorts,
    ...cleanModifiedInputPorts,
  };
  const disconnectedPortsArray = toArray(inputPortsToDisconnect).map((port) => ({
    ...port,
    outputPortId: null,
    outputNodeId: null,
  }));

  return toDict(disconnectedPortsArray);
}
