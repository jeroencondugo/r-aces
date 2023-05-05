import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { filter, map, mapTo, takeUntil } from 'rxjs/operators';
import { select, Store } from '@ngrx/store';

import { State } from '@core/reducers/permissions';
import { DialogService } from '@core/services/dialog.service';
import { NavigationActions } from '@core/actions';
import { notNull } from '@shared/utils/common.utils';
import { ClusterManagementSelectors } from '../../selectors';
import { TerminationActions } from '../../actions';
import { Termination } from '../../model/termination.model';

@Component({
  selector: 'cdg-termination-details',
  templateUrl: './termination-details.component.html',
  styleUrls: ['./termination-details.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TerminationDetailsComponent implements OnDestroy {
  termination$ = this.store.pipe(select(ClusterManagementSelectors.terminations.selected));
  unsubscribe$ = new Subject();
  showRevoke$ = this.termination$.pipe(
    notNull(),
    map(({ accepted }) => !accepted),
  );

  onEdit({ id }: Termination) {
    NavigationActions.go({ path: [`/app/cluster-mgmt/terminations/edit/${id}`] });
  }

  onAccept({ id }: Termination) {
    this.store.dispatch(TerminationActions.accept({ id }));
  }

  onDecline({ id }: Termination) {
    this.store.dispatch(TerminationActions.decline({ id }));
  }

  onRevoke({ id, client: { name } }: Termination) {
    this.dialogService
      .danger(
        'Revoke termination',
        `Are you sure you want to revoke the termination request to ${name}?`,
        'REVOKE',
        'CANCEL',
      )
      .pipe(
        filter((confirmed: boolean) => confirmed === true),
        mapTo(TerminationActions.remove({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }

  ngOnDestroy() {
    this.unsubscribe$.next(null);
  }

  constructor(private store: Store<State>, private dialogService: DialogService, private route: ActivatedRoute) {
    this.route.paramMap
      .pipe(
        map((params) => params.get('id')),
        notNull(),
        map((id) => TerminationActions.selected({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }
}
