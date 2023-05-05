import { InvitesContainer } from './invites/invites.container';
import { ClusterContainer } from './cluster/cluster.container';
import { InviteEditContainer } from './invite-edit/invite-edit.container';
import { TerminationsContainer } from './terminations/terminations.container';
import { TerminationsEditContainer } from './terminations-edit/terminations-edit.container';
import { ClusterEditContainer } from './cluster-edit/cluster-edit.container';
import { ClusterDetailComponent } from './cluster-detail/cluster-detail.component';

export const CONTAINERS = [
  ClusterContainer,
  ClusterDetailComponent,
  InvitesContainer,
  InviteEditContainer,
  TerminationsContainer,
  TerminationsEditContainer,
  ClusterEditContainer,
];
