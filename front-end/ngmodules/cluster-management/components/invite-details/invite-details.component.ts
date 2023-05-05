import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { filter, map, mapTo, takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';
import { select, Store } from '@ngrx/store';

import { NavigationActions } from '@core/actions';
import { DialogService } from '@core/services/dialog.service';
import { notNull } from '@shared/utils/common.utils';
import { State } from '@core/reducers';
import { ClusterManagementSelectors } from '../../selectors';
import { InviteActions } from '../../actions';
import { Invite } from '../../model/invite.model';

@Component({
  selector: 'cdg-invite-details',
  templateUrl: './invite-details.component.html',
  styleUrls: ['./invite-details.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InviteDetailsComponent implements OnDestroy {
  invite$ = this.store.pipe(select(ClusterManagementSelectors.invites.selected));
  showRevoke$ = this.invite$.pipe(
    notNull(),
    map(({ accepted }) => !accepted),
  );
  unsubscribe$ = new Subject();
  onEdit({ id }: Invite) {
    this.store.dispatch(NavigationActions.go({ path: [`app/cluster-mgmt/invites/${id}`] }));
  }

  onRevoke({ id, client: { name } }: Invite) {
    this.dialogService
      .danger('Revoke invitation', `Are you sure you want to revoke invitation to ${name}?`, 'REVOKE', 'CANCEL')
      .pipe(
        filter((confirmed) => confirmed === true),
        mapTo(InviteActions.remove({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }

  onAccept({ id }: Invite) {
    this.store.dispatch(InviteActions.accept({ id }));
  }
  onDecline({ id }: Invite) {
    this.store.dispatch(InviteActions.decline({ id }));
  }

  ngOnDestroy() {
    this.unsubscribe$.next(null);
  }

  constructor(private store: Store<State>, private dialogService: DialogService, private route: ActivatedRoute) {
    this.route.paramMap
      .pipe(
        map((params) => params.get('id')),
        notNull(),
        map((id) => InviteActions.selected({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }
}
