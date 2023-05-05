import { createAction, props } from '@ngrx/store';
import { FileConfig } from '../models/file.model';

export const load = createAction('[Meter Management] Load Files');
export const loadSuccess = createAction('[Meter Management] Load Files Success', props<{ files: readonly string[] }>());
export const loadFail = createAction('[Meter Management] Load Files Fail', props<{ message: string }>());
export const analyseFile = createAction('[Meter Management] Analyse File', props<{ file: string }>());
export const analyseFileSuccess = createAction('[Meter Management] Analyse File Success', props<{ config: FileConfig }>());
export const analyseFileFail = createAction('[Meter Management] Analyse File Fail', props<{ message: string }>());
