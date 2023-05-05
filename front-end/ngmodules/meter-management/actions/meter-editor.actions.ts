import { createAction, props } from '@ngrx/store';
import { Id } from '@shared/models/id.model';

enum MeterEditorActionTypes {
  OpenEditor = '[Meter Editor] Open Meter Editor',
  OpenEditorSuccess = '[Meter Editor] Open Meter Editor Success',
  CreateMeterDialog = '[Meter Editor] Open Create Meter Dialog',
}

export const openNewMeterDialog = createAction(MeterEditorActionTypes.CreateMeterDialog);
export const openMeterEditor = createAction(MeterEditorActionTypes.OpenEditor, props<{ id: Id }>());
export const openMeterEditorSuccess = createAction(MeterEditorActionTypes.OpenEditorSuccess, props<{ id: Id }>());
