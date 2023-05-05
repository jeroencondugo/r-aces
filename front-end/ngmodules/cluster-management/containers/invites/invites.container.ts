import { Component, ChangeDetectionStrategy } from '@angular/core';
import { PageEvent } from '@angular/material/paginator';
import { Store, select } from '@ngrx/store';
import { NavigationActions } from '@core/actions';
import { State } from '@core/reducers';
import { ClusterManagementSelectors } from '../../selectors';
import { Invite } from '../../model/invite.model';
import { InviteActions } from '../../actions';

@Component({
  selector: 'cdg-invites-container',
  templateUrl: './invites.container.html',
  styleUrls: ['./invites.container.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InvitesContainer {
  invites$ = this.store.pipe(select(ClusterManagementSelectors.invites.visibleInvites));
  invitesCount$ = this.store.pipe(select(ClusterManagementSelectors.invites.getCount));
  pageSize$ = this.store.pipe(select(ClusterManagementSelectors.invites.pageSize));
  page$ = this.store.pipe(select(ClusterManagementSelectors.invites.activePage));
  loading$ = this.store.pipe(select(ClusterManagementSelectors.invites.loading));
  selectedId$ = this.store.pipe(select(ClusterManagementSelectors.invites.selectedId));

  onCreateInvite() {
    this.store.dispatch(NavigationActions.go({ path: ['app/cluster-mgmt/invites/new'] }));
  }

  onInviteSelected({ id }: Invite) {
    this.store.dispatch(InviteActions.select({ id }));
  }

  onPageSelected({ pageIndex }: PageEvent) {
    this.store.dispatch(InviteActions.changePage({ page: pageIndex }));
  }

  constructor(private store: Store<State>) {}
}
