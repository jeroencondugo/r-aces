import { ChangeDetectionStrategy, Component, Inject } from '@angular/core';
import { Subject } from 'rxjs';

import { ClosableDialog } from '@core/components/overlay.component';
import { Id } from '@shared/models/id.model';
import { tokens } from '../../../structure-management/models/node-data';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'cdg-ban-dialog',
  templateUrl: './ban-dialog.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BanDialogComponent implements ClosableDialog {
  private _close$ = new Subject<{ reason: string; clientId: Id }>();

  readonly banForm = new FormGroup({
    reason: new FormControl(null, { validators: [Validators.required] }),
  });

  get close$() {
    return this._close$.asObservable();
  }

  onSubmit() {
    const reason = (this.banForm.get('reason') as FormControl).value as string;
    this._close$.next({ reason, clientId: this.data.clientId });
  }

  onCancel() {
    this._close$.next(null);
  }

  constructor(@Inject(tokens.DATA) private data: { clientId: Id }) {}
}
