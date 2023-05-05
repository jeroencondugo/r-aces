import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

import { Id } from '@shared/models/id.model';
import { Termination } from '../../model/termination.model';

@Component({
  selector: 'cdg-termination-list',
  templateUrl: './termination-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TerminationListComponent {
  @Input() terminations: Termination[];
  @Input() selectedId: Id;
  @Output() selected = new EventEmitter<Termination>();

  terminationSelected(termination: Termination) {
    this.selected.emit(termination);
  }
}
