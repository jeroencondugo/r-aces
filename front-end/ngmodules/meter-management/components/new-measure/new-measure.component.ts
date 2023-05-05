import { ChangeDetectionStrategy, Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable, Subject } from 'rxjs';
import { commonAnimations } from '@shared/animations';
import { ClosableDialog } from '@core/components/overlay.component';

interface NewMeasureContext {
  name: string;
}

@Component({
  animations: [commonAnimations.expandablePanel],
  selector: 'cdg-new-measure',
  template: `
    <mat-card>
      <form novalidate [formGroup]="form" class="new-measure" @expandablePanel (submit)="onSave(form.value)">
        <div class="expandable-content panel-container">
          <mat-form-field>
            <input matInput type="text" placeholder="Name" name="name" formControlName="name" />
          </mat-form-field>
          <div class="form-container__actions mat-card-footer">
            <button mat-button type="button" (click)="onClose()">Close</button>
            <button mat-button type="submit" [disabled]="!form.dirty">Save</button>
          </div>
        </div>
      </form>
    </mat-card>
  `,
  styles: [
    `
      .new-measure {
        padding: 16px;
        border-radius: 4px;
      }

      .panel-container {
        display: flex;
        flex-direction: column;
      }

      .form-container__actions {
        display: flex;
        justify-content: flex-end;
        margin: 8px -8px -8px;
      }

      .form-container__actions :first-child {
        margin-right: 8px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NewMeasureComponent implements ClosableDialog<NewMeasureContext> {
  form: FormGroup;

  private _close$ = new Subject<NewMeasureContext>();
  get close$(): Observable<NewMeasureContext> {
    return this._close$.asObservable();
  }

  onClose() {
    this._close$.next(null);
    this._close$.complete();
  }

  onSave(node: { name: string; label: string }) {
    this._close$.next(node);
    this._close$.complete();
  }

  constructor(private _fb: FormBuilder) {
    this.form = this._fb.group({
      name: [null, Validators.required],
    });
  }
}
