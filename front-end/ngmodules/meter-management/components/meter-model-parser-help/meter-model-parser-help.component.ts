import { Observable, Subject } from 'rxjs';
import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { ClosableDialog } from '@core/components/overlay.component';

@Component({
  selector: 'cdg-meter-model-parser-help',
  templateUrl: './meter-model-parser-help.component.html',
  styleUrls: ['./meter-model-parser-help.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MeterModelParserHelpComponent implements ClosableDialog, OnDestroy {
  private _close$ = new Subject<null>();
  get close$(): Observable<null> {
    return this._close$.asObservable();
  }

  ngOnDestroy() {
    this._close$.complete();
  }

  onClose() {
    this._close$.next();
  }
}
