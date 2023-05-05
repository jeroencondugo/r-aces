import { animate, state, style, transition, trigger } from '@angular/animations';

export const tooltipAnimation = trigger('tooltip', [
  state('void', style({ opacity: 0, transform: 'scale(0.8)' })),
  state('*', style({ opacity: 1, transform: 'scale(1)' })),
  transition('void <=> *', animate('300ms ease-in-out')),
]);
