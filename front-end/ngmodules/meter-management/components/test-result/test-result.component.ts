import { ChangeDetectionStrategy, Component, Inject } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { commonAnimations } from '@shared/animations';
import { ClosableDialog } from '@core/components/overlay.component';
import { Id } from '@shared/models/id.model';
import { Nullable } from '@shared/types/nullable.type';
import { tokens } from '../../../structure-management/models/node-data';
import { isEmpty } from '@shared/utils/common.utils';
import { DecimalPipe } from '@angular/common';
import { TestDataResults, TimeseriesDataPoint } from '../../models/test-result.model';

export interface TestResultContext {
  testData?: TestDataResults;
}

export interface TestResultReturnData {
  openMeterIdConfigs: Id;
}

@Component({
  animations: [commonAnimations.expandablePanel],
  selector: 'cdg-test-test-results',
  template: `
    <mat-card>
      <mat-card-header>
        <mat-icon svgIcon="test-tube" mat-card-avatar></mat-icon>
        <mat-card-title>{{ title }}</mat-card-title>
        <mat-card-subtitle> {{ subtitle }} </mat-card-subtitle>
      </mat-card-header>
      <mat-card-content class="test-result__content">
        <ul class="warnings-list" *ngIf="isWarning">
          <li class="warnings-list__item" *ngFor="let warning of warnings">{{ warning }}</li>
        </ul>
        <ng-container *ngIf="isInfo">
          <div class="test_result_table">
            <h2 class="mat-subheading-2"><b>Timestamp</b></h2>
            <h2 class="mat-subheading-2"><b>Value</b></h2>
            <ng-container *ngFor="let el of values">
              <p>{{ el.timestamp | date: 'dd/M/y hh:mm' }}</p>
              <p>{{ el.value | niceNumber: 'NaN' }}</p>
            </ng-container>
          </div>
        </ng-container>
      </mat-card-content>
      <mat-card-actions align="end">
        <button mat-button (click)="onClose()">CLOSE</button>
      </mat-card-actions>
    </mat-card>
  `,
  styles: ['.test_result_table { display:grid; grid-template-columns: 150px 50px; }'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [DecimalPipe],
})
export class TestResultComponent implements ClosableDialog<Nullable<TestResultReturnData>> {
  private _close$ = new Subject<Nullable<TestResultReturnData>>();
  get close$(): Observable<Nullable<TestResultReturnData>> {
    return this._close$.asObservable();
  }
  readonly isWarning: boolean;
  readonly title: string;
  readonly subtitle: string;
  readonly values: readonly TimeseriesDataPoint[];
  readonly warnings: readonly string[];
  readonly isInfo: boolean;

  onClose() {
    this._close$.next(null);
    this._close$.complete();
  }

  constructor(@Inject(tokens.DATA) private data: TestResultContext) {
    this.warnings = this.data.testData?.warnings ?? [];
    this.isWarning = !isEmpty(this.data.testData?.warnings);
    this.isInfo = data.testData?.data?.length > 0;
    this.title = this.isWarning ? 'Errors & Warnings' : `Information`;
    this.subtitle = this.isWarning ? 'Fix these or data will not be processed!' : '';
    this.values = this.data.testData?.data ?? [];
  }
}
