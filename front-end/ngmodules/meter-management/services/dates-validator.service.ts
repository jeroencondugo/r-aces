import { Injectable } from '@angular/core';
import { AbstractControl, AsyncValidator, AsyncValidatorFn, FormGroup } from '@angular/forms';
import { Observable, of } from 'rxjs';
import { isBefore } from 'date-fns';
import { toDate } from '@shared/utils/date.utils';
import { Nullable } from '@shared/types/nullable.type';
import { getValue } from '@shared/utils/form.utils';

@Injectable()
export class DatesValidatorService implements AsyncValidator {
  validate(control: AbstractControl): Observable<Nullable<{ dateError: string }>> {
    const form = control as FormGroup;
    const formValue = getValue(form);
    const beginDate = formValue('beginUtc');
    const endDate = formValue('endUtc');

    if (endDate == null || beginDate == null) {
      return of(null);
    }

    const isoBeginDate = toDate(beginDate);
    const isoEndDate = toDate(endDate);

    if (isoBeginDate == null) {
      return of({ dateError: 'Invalid begin date' });
    }

    if (isoEndDate == null) {
      return of({ dateError: 'Invalid end date' });
    }

    if (isBefore(isoEndDate, isoBeginDate)) {
      return of({ dateError: 'End date must be after begin date' });
    }

    return of(null);
  }
}

export function createDatesValidator(validatorService: DatesValidatorService): AsyncValidatorFn {
  return (control): Observable<Nullable<{ dateError: string }>> => validatorService.validate(control);
}
