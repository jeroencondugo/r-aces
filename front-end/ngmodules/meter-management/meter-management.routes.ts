import { Route } from '@angular/router';
import { CreateGuard, EditGuard } from '@core/guards/permissions.guard';
import { MeterManagementComponent } from './containers/meter-management/meter-management.component';
import { MeterCreateComponent } from './containers/meter-create/meter-create.component';
import { MeterDetailComponent } from './containers/meter-detail/meter-detail.component';
import { ConfigGraphEditorComponent } from './containers/config-graph-editor/config-graph-editor.component';
import { MeterEditComponent } from './containers/meter-edit/meter-edit.component';
import { PreventUnsavedChangesGuard } from '@core/guards/prevent-unsaved-changes.guard';

export const MeterManagementRoutes: Route[] = [
  {
    path: '',
    component: MeterManagementComponent,

    children: [
      {
        path: 'new',
        component: MeterCreateComponent,
        canActivate: [CreateGuard],
      },
      {
        path: 'edit/:id',
        component: MeterEditComponent,
        canActivate: [EditGuard],
      },
      {
        path: ':id',
        component: MeterDetailComponent,
      },
    ],
  },
  {
    path: 'config/:id',
    component: ConfigGraphEditorComponent,
    canActivate: [EditGuard],
    canDeactivate: [PreventUnsavedChangesGuard],
  },
];
