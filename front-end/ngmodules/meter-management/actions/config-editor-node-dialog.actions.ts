import { createAction, props } from '@ngrx/store';
import { Id } from '@shared/models/id.model';

enum ConfigEditorNodeDialogActionTypes {
  Reset = '[Meter Config Editor Node Dialog] Close Dialog',
  SelectOutputMode = '[Meter Config Editor Node Dialog] Select output mode',
}

export const reset = createAction(ConfigEditorNodeDialogActionTypes.Reset);

export const selectOutputMode = createAction(
  ConfigEditorNodeDialogActionTypes.SelectOutputMode,
  props<{ outputMode: string }>(),
);

export const selectMeasure = createAction('[Meter Config Editor Node Dialog] Select Measure', props<{ measure: Id }>());

export const setIsConstant = createAction(
  '[Meter Config Editor Node Dialog] Set Is Constant Value',
  props<{ field: string; isConstant: boolean }>(),
);
