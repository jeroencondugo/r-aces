import { Dict, generateUniqueId, omitKeys, sameId } from '@shared/utils/common.utils';
import { InputPortNormalized, MeterConfig, MeterConfigNormalized, OutputPortNormalized } from '../models/meter-config.model';
import { Action, createReducer, on } from '@ngrx/store';
import { GraphChangeType, NodeDeletedChangeset } from '../../structure-management/models/graph-changeset';
import { MeterConfigChangeset } from '../models/changeset.model';
import { Id } from '@shared/models/id.model';
import { MeterMgmtActions } from '../actions';
import { Nullable } from '@shared/types/nullable.type';
import { TestDataResults } from '../models/test-result.model';
import { MeterConfigMetaPort } from '../models/data.model';

export interface State {
  configs: Dict<MeterConfigNormalized>;
  configIds: readonly Id[];
  outputPorts: Dict<OutputPortNormalized>;
  inputPorts: Dict<InputPortNormalized>;
  changesetEntities: Dict<MeterConfigChangeset>;
  changesetIds: ReadonlyArray<number>;
  saving: boolean;
  historianId: Nullable<Id>;
  schema: Nullable<string>;
  table: Nullable<string>;
  tests: Dict<TestDataResults[]>;
  connectedPort: Nullable<Id>;
  navigationHistory: readonly Id[];
}

const initialState: State = {
  configs: {},
  configIds: [],
  outputPorts: {},
  inputPorts: {},
  changesetEntities: {},
  changesetIds: [],
  saving: false,
  historianId: null,
  schema: null,
  table: null,
  tests: {},
  navigationHistory: [],
  connectedPort: null,
};

const configActions = MeterMgmtActions.configEditor;

const configEditorReducer = createReducer(
  initialState,
  on(configActions.openConfigGraphEditorSuccess, (state, { id }) => {
    const currentHistory = state.navigationHistory;
    const historyIndex = currentHistory.findIndex(sameId(id));
    const existsInHistory = historyIndex >= 0;
    const navigationHistory = existsInHistory ? currentHistory.slice(0, historyIndex + 1) : [...currentHistory, id];
    return { ...state, navigationHistory };
  }),
  on(configActions.historyFromCache, (state, { navigationHistory }) => ({ ...state, navigationHistory })),
  on(configActions.editorClosed, (state) => ({ ...initialState, tests: state.tests })),
  on(configActions.deleteMeterConfig, (state, { config }) => {
    const changeId = state.changesetIds.length;
    const cleanChangesetEntities = state.changesetIds
      .map((id) => state.changesetEntities[id])
      .reduce(
        (entities, current, index) => ({
          ...entities,
          [index]: current,
        }),
        <Dict<MeterConfigChangeset>>{},
      );

    return {
      ...state,
      changesetEntities: {
        ...cleanChangesetEntities,
        [changeId]: <NodeDeletedChangeset<MeterConfig>>{
          type: GraphChangeType.NodeDeleted,
          node: config,
        },
      },
      changesetIds: [...state.changesetIds, changeId],
    };
  }),
  on(configActions.addConnection, (state, { connection, connectedPort }) => {
    const { inputPortId, outputPortId, inputNodeId: graphNodeId, outputNodeId } = connection;
    let changesetEntities = state.changesetIds
      .map((id) => state.changesetEntities[id])
      .reduce<Dict<MeterConfigChangeset>>((entities, current, index) => ({ ...entities, [index]: current }), {});
    let changesetIds = [...state.changesetIds];

    if (connectedPort) {
      const _changeId = changesetIds.length;
      changesetEntities = {
        ...changesetEntities,
        [_changeId]: {
          type: GraphChangeType.InputPortModified,
          port: {
            id: connectedPort.id,
            graphNodeId: connectedPort.graphNodeId,
            outputPortId: null,
            outputNodeId: null,
          },
        },
      };
      changesetIds = [...changesetIds, _changeId];
    }

    const changeId = changesetIds.length;

    return {
      ...state,
      changesetEntities: {
        ...changesetEntities,
        [changeId]: {
          type: GraphChangeType.InputPortModified,
          port: {
            id: inputPortId,
            graphNodeId,
            outputPortId,
            outputNodeId,
          },
        },
      },
      changesetIds: [...changesetIds, changeId],
    };
  }),
  on(configActions.deleteConnection, (state, { connection }) => {
    const [inputPortId, , graphNodeId] = connection;
    const changeId = state.changesetIds.length;
    const cleanChangesetEntities = state.changesetIds
      .map((id) => state.changesetEntities[id])
      .reduce<Dict<MeterConfigChangeset>>(
        (entities, current, index) => ({
          ...entities,
          [index]: current,
        }),
        {},
      );

    const changesetEntities = <Dict<MeterConfigChangeset>>{
      ...cleanChangesetEntities,
      [changeId]: {
        type: GraphChangeType.InputPortModified,
        port: {
          id: inputPortId,
          graphNodeId,
          outputPortId: null,
          outputNodeId: null,
        },
      },
    };
    const changesetIds = [...state.changesetIds, changeId];

    return {
      ...state,
      changesetEntities,
      changesetIds,
    };
  }),
  on(configActions.resetChanges, (state) => ({ ...state, changesetEntities: {}, changesetIds: [] })),
  on(configActions.undoChange, (state) => ({ ...state, changesetIds: state.changesetIds.slice(0, -1) || [] })),
  on(configActions.redoChange, (state) => {
    const redoId = state.changesetIds.length;
    const changesetIds = state.changesetEntities[redoId] ? [...state.changesetIds, redoId] : state.changesetIds;
    return {
      ...state,
      changesetIds,
    };
  }),
  on(configActions.loadCreateConfigSuccess, (state, { meta, config: updateValues }) => {
    const newId = `new_${generateUniqueId()}`;
    const { fields } = meta;

    const fieldsObject = fields.reduce(
      (agg, cur) => ({
        ...agg,
        [cur.name]: cur.value,
      }),
      <Dict<string | number>>{},
    );

    const portSorter = (a: MeterConfigMetaPort, b: MeterConfigMetaPort) => a.order - b.order;
    const portGenerator = ({ name }: MeterConfigMetaPort, index: number) => ({
      id: `${newId}_${index}`,
      name,
      graphNodeId: newId,
    });

    const newConfig = {
      id: newId,
      type: meta.operation,
      catalogId: meta.type,
      inputPorts: [...meta.inputPorts].sort(portSorter).map(portGenerator),
      outputPorts: [...meta.outputPorts].sort(portSorter).map(portGenerator),
      ...fieldsObject,
      ...updateValues,
    };

    const changeId = state.changesetIds.length;
    const cleanChangesetEntities = state.changesetIds
      .map((id) => state.changesetEntities[id])
      .reduce<Dict<MeterConfigChangeset>>(
        (entities, current, index) => ({
          ...entities,
          [index]: current,
        }),
        {},
      );

    const changesetEntities = {
      ...cleanChangesetEntities,
      [changeId]: {
        type: GraphChangeType.NodeAdded,
        node: newConfig,
      },
    };

    const changesetIds = [...state.changesetIds, changeId];

    return {
      ...state,
      changesetEntities,
      changesetIds,
    };
  }),
  on(configActions.updateConfig, configActions.loadEditConfigSuccess, (state, { config: node }) => {
    const changeId = state.changesetIds.length;
    const cleanChangesetEntities = state.changesetIds
      .map((id) => state.changesetEntities[id])
      .reduce<Dict<MeterConfigChangeset>>(
        (entities, current, index) => ({
          ...entities,
          [index]: current,
        }),
        {},
      );

    const changesetEntities: Dict<MeterConfigChangeset> = {
      ...cleanChangesetEntities,
      [changeId]: {
        type: GraphChangeType.NodeModified,
        node,
      },
    };

    const changesetIds = [...state.changesetIds, changeId];

    return {
      ...state,
      changesetEntities,
      changesetIds,
    };
  }),
  on(configActions.saveChanges, (state) => ({ ...state, saving: true })),
  on(
    configActions.saveChangesSuccess,
    configActions.loadConfigSuccess,
    (state, { configs, configIds, inputPorts, outputPorts, connectedPort, meterId }) => ({
      ...state,
      configs,
      configIds,
      inputPorts,
      outputPorts,
      connectedPort,
      tests: omitKeys(state.tests, [meterId]),
      changesetEntities: {},
      changesetIds: [],
      saving: false,
    }),
  ),
  on(configActions.saveChangesFail, configActions.loadConfigFail, (state) => ({ ...state, saving: false })),
  on(configActions.runTestsSuccess, (state, { dataResults, meterId }) => ({
    ...state,
    tests: { ...state.tests, [meterId]: dataResults },
  })),
);

export function reducer(state: State, action: Action): State {
  return configEditorReducer(state, action);
}
