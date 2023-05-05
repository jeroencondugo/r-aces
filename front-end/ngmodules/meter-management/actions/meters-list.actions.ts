import { createAction, props } from '@ngrx/store';
import { Id } from '@shared/models/id.model';

enum MetersListActionTypes {
  SelectId = '[Meters List] Select Meter Id',
  SelectIdSuccess = '[Meters List] Select Meter Id Success',
  SelectIdFail = '[Meters List] Select Meter Id Fail',
  SelectPage = '[Meters List] Select Page',
  SortMeters = '[Meters List] Sort Meters',
  MultiSortMeters = '[Meters List] Multi Sort Meters',
  SearchMeters = '[Meters List] Search Meters',
}

export const selectId = createAction(MetersListActionTypes.SelectId, props<{ id: Id }>());
export const selectIdSuccess = createAction(MetersListActionTypes.SelectIdSuccess, props<{ id: Id }>());
export const selectPage = createAction(MetersListActionTypes.SelectPage, props<{ page: number }>());
export const sortMeters = createAction(MetersListActionTypes.SortMeters, props<{ column: string }>());
export const multiSortMeters = createAction(MetersListActionTypes.MultiSortMeters, props<{ column: string }>());
export const searchMeters = createAction(MetersListActionTypes.SearchMeters, props<{ searchTerm: string }>());
