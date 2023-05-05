import { Component, ChangeDetectionStrategy } from '@angular/core';
import { PageEvent } from '@angular/material/paginator';
import { Store, select } from '@ngrx/store';

import { State } from '@core/reducers/permissions';
import { NavigationActions } from '@core/actions';
import { Termination } from '../../model/termination.model';
import { ClusterManagementSelectors } from '../../selectors';
import { TerminationActions } from '../../actions';

@Component({
  selector: 'cdg-terminations-container',
  templateUrl: './terminations.container.html',
  styleUrls: ['./terminations.container.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TerminationsContainer {
  page$ = this.store.pipe(select(ClusterManagementSelectors.terminations.activePage));
  terminations$ = this.store.pipe(select(ClusterManagementSelectors.terminations.visibleTerminations));
  terminationsCount$ = this.store.pipe(select(ClusterManagementSelectors.terminations.getCount));
  pageSize$ = this.store.pipe(select(ClusterManagementSelectors.terminations.getPageSize));
  loading$ = this.store.pipe(select(ClusterManagementSelectors.terminations.loading));
  selectedId$ = this.store.pipe(select(ClusterManagementSelectors.terminations.selectedId));

  onCreateTermination() {
    this.store.dispatch(NavigationActions.go({ path: ['/app/cluster-mgmt/terminations/new'] }));
  }

  onTerminationSelected({ id }: Termination) {
    this.store.dispatch(TerminationActions.select({ id }));
  }

  onPageSelected({ pageIndex }: PageEvent) {
    this.store.dispatch(TerminationActions.changePage({ page: pageIndex }));
  }

  constructor(private store: Store<State>) {}
}
