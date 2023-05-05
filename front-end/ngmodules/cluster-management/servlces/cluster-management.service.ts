import { Injectable } from '@angular/core';

import { HttpService, camelCase } from '@core/services/http.service';
import { Id } from '@shared/models/id.model';
import { ClusterNormalized } from '../model/cluster.model';

@Injectable()
export class ClusterManagementService {
  load() {
    return this.http.general.get<ClusterNormalized[]>('/cluster', camelCase.all);
  }

  create(cluster: Partial<ClusterNormalized>) {
    return this.http.general.post<ClusterNormalized>('/cluster', cluster, camelCase.all);
  }

  update(cluster: Partial<ClusterNormalized> & { id: Id }) {
    return this.http.general.patch<ClusterNormalized>(`/cluster/${cluster.id}`, cluster, camelCase.all);
  }

  delete(id: Id) {
    return this.http.general.delete<Id>(`/cluster/${id}`, camelCase.all);
  }

  ban(cluster: Id, clientIds: Id[]) {
    return this.http.general.patch(`/cluster/ban_clients/${cluster}`, { clientIds }, camelCase.all);
  }

  unban(cluster: Id, clientIds: Id[]) {
    return this.http.general.patch(`/cluster/unban_clients/${cluster}`, { clientIds }, camelCase.all);
  }

  constructor(private http: HttpService) {}
}
