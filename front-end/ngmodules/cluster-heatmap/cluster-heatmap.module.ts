import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { SharedModule } from '@shared/shared.module';
import { HeatmapLegendModule } from '@components/heatmap-legend/heatmap-legend.component';
import { ClusterHeatmapRoutes } from './cluster-heatmap.routes';
import { EFFECTS } from './effects';
import { HeatmapModule } from '@components/heatmap/heatmap.component';
import { CONTAINERS } from './containers';
import { SERVICES } from './services';
import { reducers } from './reducers';
import { HeaderTitleModule } from '@components/header-title/header-title.component';
import { ExtendedToolbarModule } from '@components/extended-toolbar/extended-toolbar.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MeasureLabelPipeModule } from '@pipes/measure-label.pipe';
import { ButtonGroupModule } from '@components/button-group/button-group.component';
import { PeriodLabelPipeModule } from '@pipes/period-label.pipe';
import { ResolutionLabelPipeModule } from '@pipes/resolution-label.pipe';
import { DatepickerModule } from '@components/datepicker/datepicker.component';
import { MatCardModule } from '@angular/material/card';
import { SpinnerModule } from '@components/spinner/spinner.component';
import { SelectNestedPipeModule } from '@pipes/select-nested.pipe';

@NgModule({
  imports: [
    SharedModule,
    RouterModule.forChild(ClusterHeatmapRoutes),
    StoreModule.forFeature('clusterHeatmap', reducers),
    EffectsModule.forFeature(EFFECTS),
    HeatmapModule,
    HeatmapLegendModule,
    HeaderTitleModule,
    ExtendedToolbarModule,
    MatToolbarModule,
    MatFormFieldModule,
    MatSelectModule,
    MeasureLabelPipeModule,
    ButtonGroupModule,
    PeriodLabelPipeModule,
    ResolutionLabelPipeModule,
    DatepickerModule,
    MatCardModule,
    SpinnerModule,
    SelectNestedPipeModule
  ],
  declarations: [...CONTAINERS],
  providers: [...SERVICES],
})
export class ClusterHeatmapModule {}
