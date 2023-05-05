import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { camelCase, HttpService } from '@core/services/http.service';
import { Id } from '@shared/models/id.model';
import { InviteFormModel, InviteNormalized } from '../model/invite.model';
import { getDaysValid } from '../utils/utils';

@Injectable()
export class InvitesService {
  load(): Observable<InviteNormalized[]> {
    return this.http.general.get<InviteNormalized[]>('/cluster_invites?expired=no', camelCase.all);
  }

  create(invite: InviteFormModel) {
    const { clients, cluster: clusterId, expiresAt } = invite;
    const daysValid = getDaysValid(expiresAt);
    const invites = clients.map((clientId) => ({ clientId, daysValid, clusterId }));

    return this.http.general.post<InviteNormalized[]>('/cluster_invites', invites, camelCase.all);
  }

  update(invite: Partial<InviteNormalized> & { id: Id }) {
    return this.http.general.patch<InviteNormalized>(`/cluster_invites/${invite.id}`, invite, camelCase.all);
  }

  delete(id: Id) {
    return this.http.general.delete<readonly InviteNormalized[]>(`/cluster_invites/${id}`, camelCase.all);
  }

  accept(id: Id) {
    return this.http.general.post<InviteNormalized>(`/cluster_invites/accept/${id}`, {}, camelCase.all);
  }

  decline(id: Id) {
    return this.http.general.post<InviteNormalized>(`/cluster_invites/deny/${id}`, {}, camelCase.all);
  }

  constructor(private http: HttpService) {}
}
