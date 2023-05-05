import { Component, Input, ChangeDetectionStrategy, Output, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { DateAdapter, MAT_DATE_FORMATS } from '@angular/material/core';
import { MAT_DATEPICKER_SCROLL_STRATEGY_FACTORY_PROVIDER } from '@angular/material/datepicker';
import { addDays } from 'date-fns';

import { SHORT_ISO_DATE_FORMATS, ShortIsoDateAdapter } from '@shared/utils/short-iso-date-adapter';
import { Id } from '@shared/models/id.model';

@Component({
  selector: 'cdg-termination-editor',
  templateUrl: './termination-editor.component.html',
  styleUrls: ['./termination-editor.component.scss'],
  providers: [
    { provide: MAT_DATE_FORMATS, useValue: SHORT_ISO_DATE_FORMATS },
    { provide: DateAdapter, useClass: ShortIsoDateAdapter },
    MAT_DATEPICKER_SCROLL_STRATEGY_FACTORY_PROVIDER,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TerminationEditorComponent {
  @Input() form: FormGroup;
  @Input() clients: { id: Id; name: string }[];
  @Input() clusters: { id: Id; name: string }[];

  @Output() selectedCluster = new EventEmitter<Id>();

  clusterSelect(selection: any) {
    this.selectedCluster.emit(selection.value);
    this.form.get('clients').reset();
  }
  minDate = addDays(new Date(), 1);
}
