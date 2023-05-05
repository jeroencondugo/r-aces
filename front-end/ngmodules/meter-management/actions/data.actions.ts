import { createAction, props } from '@ngrx/store';
import { Meter } from '@shared/models/meters';
import { MeterConfigMeta } from '../models/data.model';

enum DataActionTypes {
  LoadMeterConfigsSuccess = '[Meter Management Data] Load Meter Configs Success',
  LoadMeterConfigsFail = '[Meter Management Data] Load Meter Configs Fail',

  LoadTreeNodes = '[Meter Management Data] Load TreeNodes Request',
  LoadTreeNodesSuccess = '[Meter Management Data] Load TreeNodes Success',
  LoadTreeNodesFail = '[Meter Management Data] Load TreeNodes Fail',

  LoadMeterConfigsCatalog = '[Meter Management Data] Load Meter Configs Catalog',
  LoadMeterConfigsCatalogSuccess = '[Meter Management Data] Load Meter Configs Catalog Success',
  LoadMeterConfigsCatalogFail = '[Meter Management Data] Load Meter Configs Catalog Fail',

  ConfirmDeleteMeterAction = '[Meter Management Data] Confirm Delete Meter',
}

export const confirmDeleteMeter = createAction(DataActionTypes.ConfirmDeleteMeterAction, props<{ meter: Meter }>());

export const loadMeterConfigsCatalog = createAction(DataActionTypes.LoadMeterConfigsCatalog);
export const loadMeterConfigsCatalogSuccess = createAction(
  DataActionTypes.LoadMeterConfigsCatalogSuccess,
  props<{ catalog: ReadonlyArray<MeterConfigMeta> }>(),
);
export const loadMeterConfigsCatalogFail = createAction(
  DataActionTypes.LoadMeterConfigsCatalogFail,
  props<{ error: string }>(),
);
