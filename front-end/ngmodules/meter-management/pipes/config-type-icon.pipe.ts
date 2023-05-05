import { Pipe, PipeTransform } from '@angular/core';
import { MeterConfigMeta } from '../models/data.model';
import { getConfigIcon } from '../utils/meter-config.utils';

@Pipe({
  name: 'configTypeIcon',
  pure: true,
})
export class ConfigTypeIconPipe implements PipeTransform {
  transform(meta: MeterConfigMeta, _args?: any): string {
    return getConfigIcon(meta);
  }
}
