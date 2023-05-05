import { Pipe, PipeTransform } from '@angular/core';
import { RequestStatus } from '../model/request-status.model';
import { Dict } from '@shared/utils/common.utils';
import { ThemePalette } from '@angular/material/core';

const ICONS: Dict<ThemePalette, RequestStatus> = {
  ACCEPTED: 'primary',
  DENIED: 'warn',
  EXPIRED: 'warn',
  PENDING: 'accent',
};

@Pipe({
  name: 'statusColor',
  pure: true,
})
export class StatusColorPipe implements PipeTransform {
  transform(status: RequestStatus): ThemePalette {
    return ICONS[status];
  }
}
