import { Route } from '@angular/router';

import { EditorMode } from '@shared/models/editor-mode.model';
import { ClusterContainer } from './containers/cluster/cluster.container';
import { ClusterDetailComponent } from './containers/cluster-detail/cluster-detail.component';
import { InvitesContainer } from './containers/invites/invites.container';
import { InviteDetailsComponent } from './components/invite-details/invite-details.component';
import { InviteEditContainer } from './containers/invite-edit/invite-edit.container';
import { TerminationsContainer } from './containers/terminations/terminations.container';
import { TerminationsEditContainer } from './containers/terminations-edit/terminations-edit.container';
import { TerminationDetailsComponent } from './components/termination-details/termination-details.component';
import { ClusterEditContainer } from './containers/cluster-edit/cluster-edit.container';

export const ClusterManagementRoutes: Route[] = [
  {
    path: 'clusters',
    component: ClusterContainer,
    children: [
      {
        path: 'new',
        component: ClusterEditContainer,
        data: { mode: EditorMode.Create },
      },
      {
        path: ':id',
        component: ClusterDetailComponent,
      },
      {
        path: 'edit/:id',
        component: ClusterEditContainer,
        data: { mode: EditorMode.Edit },
      },
    ],
  },
  {
    component: InvitesContainer,
    path: 'invites',
    children: [
      {
        path: 'new',
        component: InviteEditContainer,
        data: { mode: EditorMode.Create },
      },
      {
        path: ':id',
        component: InviteDetailsComponent,
      },
    ],
  },
  {
    component: TerminationsContainer,
    path: 'terminations',
    children: [
      {
        path: 'new',
        component: TerminationsEditContainer,
        data: { mode: EditorMode.Create },
      },
      {
        path: ':id',
        component: TerminationDetailsComponent,
      },
    ],
  },
];
