import { Observable, ReplaySubject, Subject } from 'rxjs';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Inject,
  Input,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MeterConfig } from '../../models/meter-config.model';
import { notNull, omitKeys } from '@shared/utils/common.utils';
import { tokens } from '../../../structure-management/models/node-data';
import { DynamicFormComponent, FormField } from '@components/dynamic-form/dynamic-form.component';
import { createFormGroup } from '@shared/utils/form.utils';
import { map, shareReplay, startWith, switchMap, take, takeUntil } from 'rxjs/operators';
import { Nullable } from '@shared/types/nullable.type';
import { Anchor } from '@shared/models/anchor.model';
import { ClosableDialog } from '@core/components/overlay.component';
import { MeterConfigMeta } from '../../models/data.model';
import { getConfigIcon } from '../../utils/meter-config.utils';

export interface DialogContext {
  title: string;
  formProcessor: Nullable<FormProcessor>;
  metadata: MeterConfigMeta;
  anchor?: Anchor;
  removeOnSave?: readonly string[];
}

/* eslint-disable max-len */
@Component({
  selector: 'cdg-meter-config',
  template: `
    <mat-card class="meter-config">
      <mat-card-header>
        <mat-icon mat-card-avatar [svgIcon]="icon"></mat-icon>
        <mat-card-title>
          {{ title }}
        </mat-card-title>
        <button *ngIf="hasHelp" mat-icon-button (click)="onHelp()">
          <mat-icon color="primary">help</mat-icon>
        </button>
        <mat-card-subtitle> {{ subtitle }} </mat-card-subtitle>
      </mat-card-header>
      <mat-card-content *ngIf="fields$ | async as fields">
        <ng-container *ngIf="form$ | async as form">
          <cdg-dynamic-form [fields]="fields" [form]="form" #dynamicForm></cdg-dynamic-form>
          <mat-error *ngIf="form.errors?.dateError as invalidDate" class="error-wrapper">
            {{ invalidDate }}
          </mat-error>
          <mat-error *ngIf="form.errors?.invalidLimits as invalidLimits" class="error-wrapper">
            {{ invalidLimits }};
          </mat-error>
          <div class="card-footer__action-buttons">
            <button type="button" mat-button (click)="onCancel()">Cancel</button>
            <button mat-flat-button type="button" color="accent" (click)="onSave()" [disabled]="saveDisabled$ | async">
              Save
            </button>
          </div>
        </ng-container>
      </mat-card-content>
    </mat-card>
  `,
  styles: [
    `
      .meter-config {
        min-width: 340px;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MeterConfigComponent implements OnInit, OnDestroy, AfterViewInit, ClosableDialog<Partial<MeterConfig>> {
  private unsubscribe$ = new Subject();
  private _close$ = new Subject<Nullable<Partial<MeterConfig>>>();
  private _fields$ = new ReplaySubject<readonly FormField[]>(1);

  readonly close$ = this._close$.pipe(take(1), shareReplay({ refCount: true, bufferSize: 1 }));

  @Input() set fields(formFields: readonly FormField[]) {
    this._fields$.next(formFields);
  }
  @Input() hasHelp: boolean;
  @Output() helpClicked: EventEmitter<boolean> = new EventEmitter<boolean>();

  @ViewChild('dynamicForm', { static: false }) dynamicForm: DynamicFormComponent;

  readonly fields$ = this._fields$.asObservable();

  form$ = this.fields$.pipe(
    notNull(),
    take(1),
    map((fields) => createFormGroup(fields)),
    takeUntil(this.unsubscribe$),
    shareReplay({ refCount: true, bufferSize: 1 }),
  );

  saveDisabled$ = this.form$.pipe(
    switchMap((form) =>
      form.statusChanges.pipe(
        map(() => !form.dirty || !form.valid),
        startWith(true),
      ),
    ),
  );

  title: string;
  subtitle: string;
  icon: string;

  onCancel() {
    this._close$.next(null);
  }

  onHelp() {
    this.helpClicked.emit(true);
  }

  onSave() {
    this.form$
      .pipe(
        map((form) => form.getRawValue()),
        map((rawValue) => omitKeys(rawValue, this.data.removeOnSave ?? [])),
      )
      .subscribe((value) => this._close$.next(value));
  }

  ngOnInit(): void {
    this.title = this.data.title;
    this.subtitle = this.data.metadata.label;
    this.icon = getConfigIcon(this.data.metadata);
  }

  ngOnDestroy(): void {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
    this._close$.complete();
  }

  constructor(
    @Inject(tokens.DATA)
    private data: DialogContext,
  ) {}

  ngAfterViewInit(): void {
    if (this.data.formProcessor) {
      this.form$.pipe(take(1)).subscribe((form) => {
        this.data.formProcessor(form, this.unsubscribe$.asObservable(), this.dynamicForm);
      });
    }
  }
}

export type FormProcessor = (form: FormGroup, close$: Observable<any>, host: DynamicFormComponent) => void;
