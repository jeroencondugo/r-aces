import { Pipe, PipeTransform } from '@angular/core';
import { MeterType } from '@shared/models/meters';

@Pipe({
  name: 'meterType',
  pure: true,
})
export class MeterTypePipe implements PipeTransform {
  transform(value: MeterType, _args?: any): any {
    if (!value) {
      return 'N/A';
    }
    switch (value.name) {
      case 'automatic':
      case 'Automatic': {
        return 'A';
      }
      case 'manual':
      case 'Manual': {
        return 'M';
      }
      case 'virtual':
      case 'Virtual': {
        return 'V';
      }

      default:
        return 'N/A';
    }
  }
}
