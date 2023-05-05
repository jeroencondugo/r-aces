import { Component, ChangeDetectionStrategy, Input, EventEmitter, Output } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { addDays } from 'date-fns';

import { Id } from '@shared/models/id.model';
import { MatSelectChange } from '@angular/material/select';

@Component({
  selector: 'cdg-invite-editor',
  templateUrl: './invite-editor.component.html',
  styleUrls: ['./invite-editor.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InviteEditorComponent {
  @Input() form: FormGroup;
  @Input() clients: { id: Id; name: string }[];
  @Input() clusters: { id: Id; name: string }[];

  @Output() selectedCluster = new EventEmitter<Id>();

  minDate = addDays(new Date(), 1);

  clusterSelect({ value }: MatSelectChange) {
    this.selectedCluster.emit(value);
    this.form.get('clients').reset();
  }
}
