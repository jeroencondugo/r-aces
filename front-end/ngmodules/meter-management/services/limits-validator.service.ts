import { Injectable } from '@angular/core';
import { AbstractControl, AsyncValidator, AsyncValidatorFn, FormGroup } from '@angular/forms';
import { Observable, of, timer } from 'rxjs';
import { switchMap, take } from 'rxjs/operators';
import { Nullable } from '@shared/types/nullable.type';
import { getValue } from '@shared/utils/form.utils';

@Injectable()
export class LimitsValidatorService implements AsyncValidator {
  validate(control: AbstractControl): Observable<Nullable<{ invalidLimits: string }>> {
    const form = control as FormGroup;
    const formValue = getValue(form);
    const lowerLimit = formValue('lowerLimit');
    const upperLimit = formValue('upperLimit');

    if (lowerLimit == null && upperLimit == null) {
      return of({ invalidLimits: 'At least one limit must be defined' });
    }

    if (upperLimit == null || lowerLimit == null) {
      return of(null);
    }

    const validationResult =
      lowerLimit > upperLimit ? { invalidLimits: 'Lower limit must be less tan upper limit' } : null;

    return of(validationResult);
  }
}

export function createLimitsValidator(validatorService: LimitsValidatorService): AsyncValidatorFn {
  return (control): Observable<Nullable<{ invalidLimits: string }>> =>
    timer(300).pipe(
      take(1),
      switchMap(() => validatorService.validate(control)),
    );
}
