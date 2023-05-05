import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material/slide-toggle';

import { Id } from '@shared/models/id.model';
import { ClusterNormalized } from '../../model/cluster.model';

@Component({
  selector: 'cdg-cluster-list',
  template: `
    <mat-action-list>
      <button
        mat-list-item
        *ngFor="let cluster of clusters"
        (click)="onClusterSelect(cluster)"
        [ngClass]="{ 'list-item__selected': cluster | isSelected: selectedId }"
      >
        {{ cluster.name }}
        <mat-slide-toggle
          class="cluster-list-item__active-toggle"
          [checked]="cluster.active"
          [disabled]="canEdit | isFalse"
          labelPosition="before"
          (change)="onActiveChange($event, cluster)"
        >
          <mat-label>Active</mat-label>
        </mat-slide-toggle>
      </button>
    </mat-action-list>
  `,
  styles: [
    `
      .cluster-list-item__active-toggle {
        margin-left: auto;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClusterListComponent {
  @Input() clusters: ClusterNormalized[];
  @Input() selectedId: Id;
  @Input() canEdit: boolean;
  @Output() clusterSelected = new EventEmitter<ClusterNormalized>();
  @Output() activeChanged = new EventEmitter<ClusterNormalized>();

  onClusterSelect(cluster: ClusterNormalized) {
    this.clusterSelected.emit(cluster);
  }

  onActiveChange({ checked: active }: MatSlideToggleChange, cluster: ClusterNormalized) {
    this.activeChanged.emit({ ...cluster, active });
  }
}
