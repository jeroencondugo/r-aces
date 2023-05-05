import { Pipe, PipeTransform } from '@angular/core';
import { RequestStatus } from '../model/request-status.model';
import { Dict } from '@shared/utils/common.utils';

const ICONS: Dict<string, RequestStatus> = {
  ACCEPTED: 'check',
  DENIED: 'do_disturb',
  EXPIRED: 'av_timer',
  PENDING: 'pending',
};

@Pipe({
  name: 'statusIcon',
  pure: true,
})
export class StatusIconPipe implements PipeTransform {
  transform(status: RequestStatus): string {
    return ICONS[status];
  }
}
