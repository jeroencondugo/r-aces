import { ReplaySubject, Subject } from 'rxjs';
import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  OnDestroy,
  TemplateRef,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { select, Store } from '@ngrx/store';
import { debounceTime, delay, filter, map, take, takeUntil } from 'rxjs/operators';
import { Id } from '@shared/models/id.model';
import { MeasureOption, TimePeriod } from '@shared/models/filters';
import * as fromRoot from '@core/reducers';
import { ArcSankeySelectors } from '../../selectors';
import { MatSelectChange } from '@angular/material/select';
import { ArcSankeyActions } from '../../actions';
import { ArcDiagramComponent } from '@components/arc-diagram/arc-diagram.component';
import * as fromLayout from '../../../layout/reducers/layout.reducer';
import { Anchor } from '@shared/models/anchor.model';
import { GraphNode } from '@components/arc-diagram/arc-diagram.model';
import { OverlayPointService, PointOverlayContext } from '@core/services/overlay-point.service';
import { Nullable } from '@shared/types/nullable.type';
import { notNull } from '@shared/utils/common.utils';
import { tooltipAnimation } from './arc-sankey.animations';

const TOOLTIP_DELAY = 600;

@Component({
  selector: 'cdg-arc-sankey-container',
  templateUrl: './arc-sankey.container.html',
  styleUrls: ['./arc-sankey.container.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [tooltipAnimation],
})
export class ArcSankeyContainer implements OnDestroy, AfterViewInit {
  private unsubscribe$ = new Subject();
  private tooltip$ = new ReplaySubject<Nullable<Anchor & { node: GraphNode }>>(1);

  @ViewChild('arcDiagram', { static: true }) arcDiagram: ArcDiagramComponent;
  @ViewChild('tooltipTemplate') tooltipTemplate: TemplateRef<PointOverlayContext<GraphNode>>;

  sites$ = this._store.pipe(select(ArcSankeySelectors.sites.getList));
  selectedSiteId$ = this._store.pipe(select(ArcSankeySelectors.filter.getSiteId));
  loading$ = this._store.pipe(select(ArcSankeySelectors.data.getLoading));
  startDate$ = this._store.pipe(select(ArcSankeySelectors.filter.getStartDate));
  availablePeriods$ = this._store.pipe(select(ArcSankeySelectors.filter.getPeriods));
  selectedPeriod$ = this._store.pipe(select(ArcSankeySelectors.filter.getSelectedPeriod));
  datetimeOptions$ = this._store.pipe(select(ArcSankeySelectors.filter.getDatetimeOptions));

  minDate$ = this._store.pipe(
    select(ArcSankeySelectors.filter.getFilterDateRange),
    map(({ startDate }) => startDate),
  );

  maxDate$ = this._store.pipe(
    select(ArcSankeySelectors.filter.getFilterDateRange),
    map(({ endDate }) => endDate),
  );

  previousDisabled$ = this._store.pipe(select(ArcSankeySelectors.filter.getPreviousDisabled));
  nextDisabled$ = this._store.pipe(select(ArcSankeySelectors.filter.getNextDisabled));
  filterActionsVisible$ = this._store.pipe(select(ArcSankeySelectors.filter.getIsValidConfig));
  data$ = this._store.pipe(select(ArcSankeySelectors.data.getData));
  hasData$ = this._store.pipe(select(ArcSankeySelectors.data.hasData));
  availableMeasureOptions$ = this._store.pipe(select(ArcSankeySelectors.filter.getMeasureOptions));
  measureOptionsDisabled$ = this.availableMeasureOptions$.pipe(map(({ length }) => length <= 1));
  selectedMeasureOption$ = this._store.pipe(select(ArcSankeySelectors.filter.getSelectedMeasureOption));

  onSiteSelected({ value }: MatSelectChange) {
    const id = value as Id;
    this._store.dispatch(ArcSankeyActions.filter.selectSite({ id }));
  }

  onChangeStartDate(date: Date) {
    this._store.dispatch(ArcSankeyActions.filter.selectStartDate({ date: date.toISOString() }));
  }

  onPeriodSelect({ value }: MatSelectChange) {
    const period = value as TimePeriod;
    this._store.dispatch(ArcSankeyActions.filter.selectPeriod({ period }));
  }

  onDecrementStartDate() {
    this.startDate$
      .pipe(
        take(1),
        map((date) => ArcSankeyActions.filter.decrementDate({ date: date.toISOString() })),
      )
      .subscribe(this._store);
  }

  onIncrementStartDate() {
    this.startDate$
      .pipe(
        take(1),
        map((date) => ArcSankeyActions.filter.incrementDate({ date: date.toISOString() })),
      )
      .subscribe(this._store);
  }

  onMeasureOptionSelect({ value }: MatSelectChange) {
    const measureOption = value as MeasureOption;
    this._store.dispatch(ArcSankeyActions.filter.selectMeasure({ measureOption }));
  }

  updateTooltip(tooltipEvent: Anchor & { node: GraphNode }) {
    this.tooltip$.next(tooltipEvent);
  }

  ngAfterViewInit(): void {
    this._store.pipe(select(fromLayout.getShowSidenav), takeUntil(this.unsubscribe$)).subscribe(() => {
      if (this.arcDiagram != null) {
        this.arcDiagram.redrawGraph();
      }
    });

    this.tooltip$.pipe(debounceTime(TOOLTIP_DELAY), notNull(), takeUntil(this.unsubscribe$)).subscribe((tooltip) => {
      this.pointOverlay.open(tooltip, tooltip?.node, this.tooltipTemplate, this.viewContainerRef, false, [
        { originX: 'end', originY: 'bottom', overlayX: 'start', overlayY: 'bottom' },
        { originX: 'end', originY: 'bottom', overlayX: 'end', overlayY: 'bottom' },
        { originX: 'end', originY: 'bottom', overlayX: 'center', overlayY: 'bottom' },
      ]);
    });

    this.tooltip$
      .pipe(
        filter((tooltip) => tooltip == null),
        delay(TOOLTIP_DELAY),
      )
      .subscribe(() => {
        this.pointOverlay.close();
      });
  }

  ngOnDestroy(): void {
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
  }

  constructor(
    private _store: Store<fromRoot.State>,
    private pointOverlay: OverlayPointService,
    private viewContainerRef: ViewContainerRef,
  ) {}
}
