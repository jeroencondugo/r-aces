import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { EffectsModule } from '@ngrx/effects';
import { StoreModule } from '@ngrx/store';
import { SharedModule } from '@shared/shared.module';
import { MeterManagementRoutes } from './meter-management.routes';
import { reducers } from './reducers';
import { COMPONENTS } from './components';
import { CONTAINERS } from './containers';
import { PIPES } from './pipes';
import { EFFECTS } from './effects';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatListModule } from '@angular/material/list';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatBadgeModule } from '@angular/material/badge';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { A11yModule } from '@angular/cdk/a11y';
import { GraphModule } from '../graph/graph.module';
import { DropdownSearchModule } from '@components/dropdown-search/dropdown-search.component';
import { SortingModule } from '@components/sorting/sorting.component';
import { MatRippleModule } from '@angular/material/core';
import { SparklineMiniModule } from '@components/sparkline/sparkline-mini.component';
import { SpinnerModule } from '@components/spinner/spinner.component';
import { HeaderTitleModule } from '@components/header-title/header-title.component';
import { DynamicFormModule } from '@components/dynamic-form/dynamic-form.component';
import { ExtendedToolbarModule } from '@components/extended-toolbar/extended-toolbar.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { SERVICES } from './services';
import { IsSelectedPipeModule } from '@pipes/is-selected.pipe';
import { ControlErrorModule } from '@directives/control-error/control-error.directive';
import { IsEmptyPipeModule } from '@pipes/is-empty.pipe';
import { MeasureLabelPipeModule } from '@pipes/measure-label.pipe';
import { MultiSortOrderPipeModule } from '@pipes/multi-sort-order.pipe';
import { SortByColumnPipeModule } from '@pipes/sort-by-column.pipe';
import { PermissionModule } from '@directives/permission/permission.directive';
import { OverlayModule } from '@angular/cdk/overlay';
import { NiceNumberPipeModule } from '@pipes/nice-number.pipe';
import { TruncatePipeModule } from '@pipes/truncate.pipe';
import { MatTooltipModule } from '@angular/material/tooltip';
import { IsFalsePipeModule } from '@pipes/is-false.pipe';
import { MeterFormModule } from '@components/meter-form/meter-form.component';

const MATERIAL_MODULES = [
  A11yModule,
  MatBadgeModule,
  MatButtonModule,
  MatCardModule,
  MatCheckboxModule,
  MatChipsModule,
  MatExpansionModule,
  MatFormFieldModule,
  MatIconModule,
  MatInputModule,
  MatListModule,
  MatPaginatorModule,
  MatRippleModule,
  MatSelectModule,
  MatTableModule,
  MatToolbarModule,
];

const COMPONENTS_MODULES = [
  DropdownSearchModule,
  DynamicFormModule,
  ExtendedToolbarModule,
  GraphModule,
  HeaderTitleModule,
  IsSelectedPipeModule,
  SortingModule,
  SparklineMiniModule,
  SpinnerModule,
  ControlErrorModule,
  IsEmptyPipeModule,
  MeasureLabelPipeModule,
  MultiSortOrderPipeModule,
  SortByColumnPipeModule,
  PermissionModule,
  MeterFormModule,
];

@NgModule({
  imports: [
    SharedModule,
    ...MATERIAL_MODULES,
    ...COMPONENTS_MODULES,
    RouterModule.forChild([...MeterManagementRoutes]),
    StoreModule.forFeature('meter-management', reducers),
    EffectsModule.forFeature(EFFECTS),
    OverlayModule,
    NiceNumberPipeModule,
    TruncatePipeModule,
    MatTooltipModule,
    IsFalsePipeModule,
  ],
  declarations: [...COMPONENTS, ...CONTAINERS, ...PIPES],
  providers: [...SERVICES],
})
export class MeterManagementModule {}
