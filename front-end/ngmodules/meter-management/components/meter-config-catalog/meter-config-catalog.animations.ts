import { animate, group, query, sequence, state, style, transition, trigger } from '@angular/animations';

export const configMenuAnimation = trigger('configMenu', [
  state('void', style({ opacity: 0, transform: 'scale(0.01, 0.01)' })),
  transition(
    ':enter',
    sequence([
      query('.config-picker-container', style({ opacity: 0 })),
      animate('100ms linear', style({ opacity: 1, transform: 'scale(1, 0.5)' })),
      group([
        query('.config-picker-container', animate('400ms cubic-bezier(0.55, 0, 0.55, 0.2)', style({ opacity: 1 }))),
        animate('300ms cubic-bezier(0.25, 0.8, 0.25, 1)', style({ transform: 'scale(1, 1)' })),
      ]),
    ]),
  ),
  transition(':leave', [
    // TODO: Waiting for material fix - follow pull req: https://github.com/angular/material2/pull/11778
    // bug: https://github.com/angular/material2/issues/11765
    // animate('150ms 50ms linear', style({ opacity: 0 }))
  ]),
]);
