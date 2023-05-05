import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatCardModule } from '@angular/material/card';
import { LayoutModule } from '@angular/cdk/layout';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { RouterModule } from '@angular/router';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';

import { PermissionModule } from '@directives/permission/permission.directive';
import { IsSelectedPipeModule } from '@pipes/is-selected.pipe';
import { ExtendedToolbarModule } from '@components/extended-toolbar/extended-toolbar.component';
import { HeaderTitleModule } from '@components/header-title/header-title.component';
import { SpinnerModule } from '@components/spinner/spinner.component';
import { reducers } from './reducers';
import { EFFECTS } from './effects';
import { COMPONENTS } from './components';
import { CONTAINERS } from './containers';
import { SERVICES } from './servlces';
import { ClusterManagementRoutes } from './cluster-management.routes';
import { BooleanLabelsPipeModule } from '@pipes/boolean-labels.pipe';
import { SharedModule } from '@shared/shared.module';
import { DistanceInWordsToNowPipeModule } from '@pipes/distance-in-words-to-now.pipe';
import { PIPES } from './pipes';
import { IsFalsePipeModule } from '@pipes/is-false.pipe';

const MATERIAL_MODULES = [
  MatButtonModule,
  MatDialogModule,
  LayoutModule,
  MatIconModule,
  MatInputModule,
  MatToolbarModule,
  MatCardModule,
  MatListModule,
  MatFormFieldModule,
  MatSelectModule,
  MatSlideToggleModule,
  MatPaginatorModule,
  MatTooltipModule,
  MatDatepickerModule,
  MatNativeDateModule,
];

const IMPORTED_MODULES = [ExtendedToolbarModule, PermissionModule, HeaderTitleModule, IsSelectedPipeModule];

@NgModule({
  imports: [
    SharedModule,
    ...IMPORTED_MODULES,
    ...MATERIAL_MODULES,
    RouterModule.forChild([...ClusterManagementRoutes]),
    StoreModule.forFeature('cluster-management', reducers),
    EffectsModule.forFeature(EFFECTS),
    SpinnerModule,
    BooleanLabelsPipeModule,
    DistanceInWordsToNowPipeModule,
    IsFalsePipeModule
  ],
  providers: [SERVICES],
  declarations: [...CONTAINERS, ...COMPONENTS, ...PIPES],
})
export class ClusterManagementModule {}
