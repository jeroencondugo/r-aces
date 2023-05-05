import { MeterConfig, NormalizedConfigsData } from '../models/meter-config.model';
import { Id } from '@shared/models/id.model';
import { MeterConfigMeta } from '../models/data.model';
import { ChangesDTO } from '../models/changeset.model';

import { createAction, props } from '@ngrx/store';
import { Connection } from '../../graph/model/connection.model';
import { FailPayload } from '@shared/models/fail-payload.model';
import { TestDataResults } from '../models/test-result.model';

const LABEL = '[Meter Config Editor]';

export const openConfigGraphEditor = createAction(`${LABEL} Open Config Graph Editor`, props<{ id: Id }>());
export const openConfigGraphEditorSuccess = createAction(
  `${LABEL} Open Config Graph Editor Success`,
  props<{ id: Id }>(),
);

export const navigateBack = createAction(`${LABEL} Navigate Back`);
export const editorClosed = createAction(`${LABEL} Close Config Graph Editor Success`);
export const deleteMeterConfig = createAction(`${LABEL} Delete Meter Config`, props<{ config: MeterConfig }>());

export const loadEditConfig = createAction(
  `${LABEL} Loading Edit config from BE`,
  props<{ oldConfig: MeterConfig; newConfig: Partial<MeterConfig> }>(),
);
export const loadEditConfigSuccess = createAction(
  `${LABEL} Loading Edit Config Success`,
  props<{ config: Partial<MeterConfig> }>(),
);
export const loadEditConfigFail = createAction(`${LABEL} Loading Edit Config Fail`, props<{ error: string }>());

export const updateConfig = createAction(`${LABEL} Update Meter Config`, props<{ config: Partial<MeterConfig> }>());

export const updateConfigFail = createAction(`${LABEL} Update Meter Config Fail`, props<{ error: string }>());

export const loadCreateConfig = createAction(
  `${LABEL} Load Create Meter Config`,
  props<{ config: Partial<MeterConfig>; meta: MeterConfigMeta }>(),
);

export const loadCreateConfigSuccess = createAction(
  `${LABEL}  Load Create Meter Config Success`,
  props<{ config: Partial<MeterConfig>; meta: MeterConfigMeta }>(),
);

export const loadCreateConfigFail = createAction(`${LABEL} Load Create Meter Config Fail`, props<{ error: string }>());

export const addConnection = createAction(
  `${LABEL} Add Connection`,
  props<{ connection: Connection; connectedPort?: { id: Id; graphNodeId: Id } }>(),
);

export const deleteConnection = createAction(`${LABEL} Delete Connection`, props<{ connection: [Id, Id, Id, Id] }>());

export const undoChange = createAction(`${LABEL} Undo Change`);
export const redoChange = createAction(`${LABEL} Redo Change`);
export const resetChanges = createAction(`${LABEL} Reset Change`);

export const generateLayoutFailed = createAction(
  `${LABEL} Generate Layout Failed`,
  props<{ error: string; hasChanges: boolean }>(),
);

export const saveChanges = createAction(`${LABEL} Save changes`, props<{ changes: ChangesDTO }>());
export const saveChangesSuccess = createAction(
  `${LABEL} Save changes Success`,
  props<NormalizedConfigsData & { connectedPort: Id; meterId: Id }>(),
);

export const saveChangesFail = createAction(`${LABEL} Save changes Fail`, props<{ error: string }>());

export const loadConfigSuccess = createAction(
  `${LABEL} Load config Success`,
  props<NormalizedConfigsData & { connectedPort: Id; meterId: Id }>(),
);

export const loadConfigFail = createAction(`${LABEL} Load config Fail`, props<{ error: string }>());

export const runTests = createAction(`${LABEL} Run tests`, props<{ meterId: Id }>());
export const runTestsSuccess = createAction(
  `${LABEL} Run tests success`,
  props<{ meterId: Id; dataResults: TestDataResults[] }>(),
);
export const runTestsFail = createAction(`${LABEL} Run tests fail`, props<FailPayload>());

export const historyFromCache = createAction(
  `${LABEL} Navigation history loaded from cache`,
  props<{ navigationHistory: readonly Id[] }>(),
);
