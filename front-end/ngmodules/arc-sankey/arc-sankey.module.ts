import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';

import { SharedModule } from '@shared/shared.module';
import { reducers } from './reducers';
import { CONTAINERS } from './containers';
import { SERVICES } from './services';
import { EFFECTS } from './effects';
import { ArcSankeyRoutes } from './arc-sankey.routes';
import { HeaderTitleModule } from '@components/header-title/header-title.component';
import { ExtendedToolbarModule } from '@components/extended-toolbar/extended-toolbar.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { PeriodLabelPipeModule } from '@pipes/period-label.pipe';
import { DatepickerModule } from '@components/datepicker/datepicker.component';
import { SpinnerModule } from '@components/spinner/spinner.component';
import { MatCardModule } from '@angular/material/card';
import { ArcDiagramModule } from '@components/arc-diagram/arc-diagram.component';
import { CapitalCasePipeModule } from '@pipes/capital-case.pipe';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { NiceNumberPipeModule } from '@pipes/nice-number.pipe';
import { DecimalPipe } from '@angular/common';

@NgModule({
  imports: [
    SharedModule,
    RouterModule.forChild(ArcSankeyRoutes),
    StoreModule.forFeature('arc-sankey', reducers),
    EffectsModule.forFeature(EFFECTS),
    HeaderTitleModule,
    ExtendedToolbarModule,
    MatToolbarModule,
    MatFormFieldModule,
    MatSelectModule,
    PeriodLabelPipeModule,
    DatepickerModule,
    SpinnerModule,
    MatCardModule,
    ArcDiagramModule,
    CapitalCasePipeModule,
    MatListModule,
    MatIconModule,
    NiceNumberPipeModule,
  ],
  declarations: [...CONTAINERS],
  providers: [...SERVICES, DecimalPipe],
})
export class ArcSankeyModule {}
