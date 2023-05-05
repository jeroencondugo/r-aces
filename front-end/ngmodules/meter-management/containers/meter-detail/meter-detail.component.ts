import { combineLatest, Observable, Subscription } from 'rxjs';
import { map, take } from 'rxjs/operators';
import { ChangeDetectionStrategy, Component, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { select, Store } from '@ngrx/store';

import * as fromMeterManagement from '../../reducers';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { Dict, isEmpty } from '@shared/utils/common.utils';
import { Meter } from '@shared/models';
import { MeterMgmtActions } from '../../actions';
import { MetersListSelectors } from '../../selectors';
import { DataSelectors } from '@data/selectors';

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'cdg-meter-detail',
  styles: [
    `
      .meter {
        margin-top: 16px;
      }

      .meter-field {
        display: flex;
        margin: 16px;
        align-items: center;
        justify-content: space-between;
      }

      .meter-field__label {
        opacity: 0.8;
      }
    `,
  ],
  animations: [
    trigger('fadeIn', [
      state('void', style({ opacity: 0 })),
      state('*', style({ opacity: 1 })),
      transition('void <=> *', animate('300ms ease-in-out')),
    ]),
  ],
  template: `
    <mat-card *ngIf="selectedMeter$ | async as selectedMeter" [@fadeIn]="">
      <mat-card-header>
        <mat-card-title>{{ selectedMeter.name }}</mat-card-title>
      </mat-card-header>
      <mat-divider [inset]="true"></mat-divider>
      <mat-card-content class="meter">
        <section class="meter-field">
          <mat-label class="meter-field__label mat-body-1">ID</mat-label>
          <span class="meter-field_value mat-body-2">{{ selectedMeter.id || 'N/A' }}</span>
        </section>
        <section class="meter-field">
          <mat-label class="meter-field__label mat-body-1">Name</mat-label>
          <span class="meter-field_value mat-body-2">{{ selectedMeter.name || 'N/A' }}</span>
        </section>
        <section class="meter-field">
          <mat-label class="meter-field__label mat-body-1">Measure</mat-label>
          <span class="meter-field_value mat-body-2">{{ selectedMeter.measure | measureLabel }}</span>
        </section>
        <section class="meter-field" *ngFor="let connection of connections$ | async">
          <mat-label class="meter-field__label mat-body-1">
            {{ connection.basetree }}
          </mat-label>
          <span class="meter-field_value mat-body-2"> {{ connection.node || 'none' }} </span>
        </section>
        <mat-divider [inset]="true"></mat-divider>
        <div class="card-footer__action-buttons">
          <button mat-button (click)="onEditMeter()">EDIT</button>
          <button mat-button color="warn" (click)="onDeleteMeter(selectedMeter)">DELETE</button>
        </div>
      </mat-card-content>
    </mat-card>
  `,
})
export class MeterDetailComponent implements OnDestroy {
  private _subscription: Subscription;
  selectedMeter$ = this._store.pipe(select(fromMeterManagement.getSelectedMeter));
  basetrees$ = this._store.pipe(select(DataSelectors.basetrees.getList));
  treeNodes$ = this._store.pipe(select(DataSelectors.nodes.getEntities));

  connections$: Observable<{ basetree: string; node: string }[]> = combineLatest([
    this.selectedMeter$,
    this.basetrees$,
    this.treeNodes$,
  ]).pipe(
    map(([meter, basetrees, nodes]) => {
      if (meter == null || meter.nodes == null || isEmpty(basetrees) || isEmpty(nodes)) {
        return [];
      }

      const initBasetrees = basetrees.reduce(
        (acc, basetree) => ({ ...acc, [basetree.id]: { node: null, basetree: basetree.name } }),
        <Dict<{ basetree: string; node: string | null }>>{},
      );
      const connections = meter.nodes.reduce(
        (acc, conn) => ({
          ...acc,
          [conn.basetreeId]: {
            ...acc[conn.basetreeId],
            node: nodes[conn.nodeId] ? nodes[conn.nodeId].name : null,
          },
        }),
        initBasetrees,
      );

      return Object.keys(connections).map((key) => connections[key]);
    }),
  );

  onEditMeter() {
    this._store
      .pipe(
        select(MetersListSelectors.getSelectedId),
        take(1),
        map((id) => MeterMgmtActions.meterEditor.openMeterEditor({ id })),
      )
      .subscribe(this._store);
  }

  onDeleteMeter(meter: Meter) {
    this._store.dispatch(MeterMgmtActions.data.confirmDeleteMeter({ meter }));
  }

  ngOnDestroy(): void {
    this._subscription.unsubscribe();
  }

  constructor(private _store: Store<fromMeterManagement.State>, private _route: ActivatedRoute) {
    this._subscription = this._route.paramMap
      .pipe(
        map((params) => params.get('id')),
        map((id) => MeterMgmtActions.metersList.selectIdSuccess({ id })),
      )
      .subscribe(this._store);
  }
}
