import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'cdg-cluster-editor',
  template: `
    <form [formGroup]="form">
      <mat-form-field class="cluster-edit__field">
        <mat-label>Name</mat-label>
        <input matInput type="text" placeholder="Name" formControlName="name" />
      </mat-form-field>
      <section class="cluster-edit__item">
        <mat-label>Active</mat-label>
        <mat-slide-toggle formControlName="active" class="cluster-edit-item__slider"></mat-slide-toggle>
      </section>
    </form>
  `,
  styles: [
    `
      .cluster-edit__item {
        display: flex;
      }
      .cluster-edit-item__slider {
        margin-left: auto;
      }
      .cluster-edit__field {
        display: block;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClusterEditorComponent {
  @Input() form: FormGroup;
}
