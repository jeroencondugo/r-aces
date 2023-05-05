import { Injectable } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { Nullable } from '@shared/types/nullable.type';
import { camelCase, HttpService } from '@core/services/http.service';

@Injectable()
export class ParserValidatorService {
  validate(formula: string): Observable<Nullable<{ invalidFormula: string }>> {
    return this._http
      .post<{ isValid: boolean; warning: string }>(
        '/meter_model/validate_parser_formula',
        { formula },
        camelCase.response,
      )
      .pipe(map((result) => (result.isValid ? null : { invalidFormula: result.warning })));
  }

  constructor(private _http: HttpService) {}
}

export const createParserValidator = (validatorService: ParserValidatorService) => (input: FormControl) =>
  validatorService.validate(input.value);
