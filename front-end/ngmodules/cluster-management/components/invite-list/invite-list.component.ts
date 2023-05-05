import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

import { Id } from '@shared/models/id.model';
import { Invite } from '../../model/invite.model';

@Component({
  selector: 'cdg-invite-list',
  templateUrl: './invite-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InviteListComponent {
  @Input() invites: Invite[];
  @Input() selectedId: Id;
  @Output() selected = new EventEmitter<Invite>();

  inviteSelected(invite: Invite) {
    this.selected.emit(invite);
  }

  inviteIdentity(_index: number, item: Invite) {
    return item.id;
  }
}
