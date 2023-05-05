import { AutonameService } from './autoname.service';
import { DatesValidatorService } from './dates-validator.service';
import { LimitsValidatorService } from './limits-validator.service';
import { ParserValidatorService } from './parser-validator.service';
import { TableNameValidatorService } from './database-table-validator.service';

export const SERVICES = [
  AutonameService,
  DatesValidatorService,
  LimitsValidatorService,
  ParserValidatorService,
  TableNameValidatorService,
];
