import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { Meter, Sorting } from '@shared/models';
import { Id } from '@shared/models/id.model';

@Component({
  selector: 'cdg-meters-list',
  styleUrls: ['./meters-list.component.scss'],
  templateUrl: './meters-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MetersListComponent {
  @Input() meters: readonly Meter[] = [];
  @Input() displayedColumns: ReadonlyArray<string>;
  @Input() sorting: ReadonlyArray<{ key: string; order: Sorting }> = [];
  @Input() selectedId: Id;

  @Output() meterSelected = new EventEmitter<Id>();
  @Output() metersSingleSort: EventEmitter<string> = new EventEmitter<string>();
  @Output() metersMultiSort: EventEmitter<string> = new EventEmitter<string>();

  onMetersSingleSort(sortColumn: string) {
    this.metersSingleSort.next(sortColumn);
  }

  onMetersMultiSort(sortColumn: string) {
    this.metersMultiSort.next(sortColumn);
  }
}
