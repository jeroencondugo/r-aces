import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { Id } from '@shared/models/id.model';

export interface Breadcrumb {
  id: Id;
  name: string;
}

@Component({
  selector: 'cdg-config-breadcrumbs',
  template: `
    <ng-container *ngFor="let breadcrumb of breadcrumbs; let last = last">
      <button
        mat-button
        color="primary"
        [disabled]="last"
        (click)="onNavigateToBreadcrumb(breadcrumb.id)"
        [matTooltipDisabled]="breadcrumb.name.length < 15"
        [matTooltip]="breadcrumb.name"
      >
        {{ breadcrumb.name | truncate: 15 }}
      </button>
      <mat-icon class="breadcrumb__arrow" *ngIf="!last"> arrow_right </mat-icon>
    </ng-container>
  `,
  styleUrls: ['./config-breadcrumbs.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigBreadcrumbsComponent {
  @Input() breadcrumbs: readonly Breadcrumb[];
  @Output() navigate: EventEmitter<Id> = new EventEmitter<Id>();

  onNavigateToBreadcrumb(id: Id) {
    this.navigate.emit(id);
  }
}
