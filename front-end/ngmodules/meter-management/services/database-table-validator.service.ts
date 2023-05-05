import { Observable, of } from 'rxjs';
import { Nullable } from '@shared/types/nullable.type';
import { FormControl } from '@angular/forms';
import { omitKeys } from '@shared/utils/common.utils';

export class TableNameValidatorService {
  validate(tableName: string): Observable<Nullable<{ invalidTableName: string }>> {
    const validation = VALIDATORS.find(({ check }) => check(tableName));
    return validation ? of(omitKeys(validation, ['check'])) : of(null);
  }
}

const VALIDATORS: { check: (name: string) => boolean; invalidTableName: string }[] = [
  { check: (name) => name === '', invalidTableName: 'Table name cannot be empty' },
  { check: (name) => /\s/.test(name), invalidTableName: 'Table name cannot contain whitespaces' },
  {
    check: (name) => /[^A-Za-z0-9_?.-]/.test(name),
    invalidTableName: 'Cannot use special characters in table name!',
  },
];

export const createTableNameValidator = (validatorService: TableNameValidatorService) => (input: FormControl) =>
  validatorService.validate(input.value);
