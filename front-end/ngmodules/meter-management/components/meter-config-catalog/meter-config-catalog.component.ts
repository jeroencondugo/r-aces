import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnDestroy,
  Output,
  TemplateRef,
  ViewChild,
  ViewContainerRef,
} from '@angular/core';
import { configMenuAnimation } from './meter-config-catalog.animations';
import { Overlay, OverlayRef } from '@angular/cdk/overlay';
import { TemplatePortal } from '@angular/cdk/portal';
import { ESCAPE } from '@angular/cdk/keycodes';
import { filter, take, takeUntil } from 'rxjs/operators';
import { merge, Subject } from 'rxjs';
import { AnimationEvent } from '@angular/animations';
import { isKeyCode } from '@shared/utils/common.utils';
import { MeterConfigMeta } from '../../models/data.model';

@Component({
  selector: 'cdg-meter-config-catalog',
  templateUrl: './meter-config-catalog.component.html',
  styleUrls: ['./meter-config-catalog.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [configMenuAnimation],
})
export class MeterConfigCatalogComponent implements OnDestroy {
  isOpen = false;

  private destroy$ = new Subject();

  private _overlayRef: OverlayRef;
  private get overlayRef(): OverlayRef {
    return this._overlayRef;
  }
  private set overlayRef(value: OverlayRef) {
    if (this._overlayRef) {
      this._overlayRef.dispose();
    }
    this._overlayRef = value;
  }

  @ViewChild('trigger', { read: ElementRef }) trigger: ElementRef;
  @ViewChild('element') element: ElementRef;
  @ViewChild('dialogTpl') dialogTpl: TemplateRef<HTMLElement>;

  @Input() configsByCategory: readonly { name: string; configs: readonly MeterConfigMeta[] }[] = [];
  @Output() configSelected: EventEmitter<MeterConfigMeta> = new EventEmitter<MeterConfigMeta>();

  constructor(private overlay: Overlay, private viewContainerRef: ViewContainerRef) {}

  onConfigSelect(type: MeterConfigMeta) {
    this.closeDialog();
    this.configSelected.next(type);
  }

  openDialog() {
    const portal = new TemplatePortal<any>(this.dialogTpl, this.viewContainerRef);

    this.overlayRef = this.overlay.create({
      positionStrategy: this.overlay
        .position()
        .flexibleConnectedTo(this.trigger)
        .withPositions([
          { overlayX: 'start', overlayY: 'top', originX: 'end', originY: 'top' },
          { overlayX: 'end', overlayY: 'top', originX: 'end', originY: 'top' },
          { overlayX: 'start', overlayY: 'bottom', originX: 'end', originY: 'center' },
          { overlayX: 'end', overlayY: 'bottom', originX: 'end', originY: 'center' },
        ])
        .withFlexibleDimensions(true)
        .withGrowAfterOpen(true)
        .withViewportMargin(24),
      hasBackdrop: true,
      maxHeight: '90vh',
    });

    this.overlayRef.attach(portal);

    merge(
      this.overlayRef.backdropClick(),
      this.overlayRef.keydownEvents().pipe(filter((event) => isKeyCode(event, ESCAPE))),
    )
      .pipe(takeUntil(this.destroy$), take(1))
      .subscribe(() => this.closeDialog());
  }

  closeDialog() {
    if (this.overlayRef) {
      this.overlayRef.detach();
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.overlayRef) {
      this.overlayRef.detach();
    }
  }

  onAnimationDone(event: AnimationEvent) {
    if (event.fromState === 'opened' && event.toState === 'void' && this.overlayRef != null) {
      this.overlayRef.dispose();
    }
  }
}
