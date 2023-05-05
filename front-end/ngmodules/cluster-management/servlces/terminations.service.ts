import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';

import { camelCase, HttpService } from '@core/services/http.service';
import { Id } from '@shared/models/id.model';
import { TerminationForm, TerminationNormalized } from '../model/termination.model';
import { getDaysValid } from '../utils/utils';
import { select, Store } from '@ngrx/store';
import * as fromRoot from '@core/reducers';
import * as fromAuth from '../../auth/reducers';
import { concatMap, take } from 'rxjs/operators';
import { HttpParams } from '@angular/common/http';

@Injectable()
export class TerminationsService {
  load(): Observable<TerminationNormalized[]> {
    return this.store.pipe(
      select(fromAuth.getSelectedDomainId),
      take(1),
      concatMap((domainId) =>
        this.http.general.get<TerminationNormalized[]>('/cluster_terminations', {
          params: new HttpParams({ fromObject: { domain_id: `${domainId}`, expired: 'no' } }),
          ...camelCase.all,
        }),
      ),
    );
  }

  create(termination: TerminationForm) {
    const { clients, cluster: clusterId, expiresAt } = termination;
    const daysValid = getDaysValid(expiresAt);
    const terminations = clients.map((clientId) => ({ clientId, clusterId, daysValid }));

    return this.http.general.post<TerminationNormalized[]>('/cluster_terminations', terminations, camelCase.all);
  }

  update(invite: Partial<TerminationNormalized> & { id: Id }) {
    return this.http.general.patch<TerminationNormalized>(`/cluster_terminations/${invite.id}`, invite, camelCase.all);
  }

  delete(id: Id) {
    return this.http.general.delete<readonly TerminationNormalized[]>(`/cluster_terminations/${id}`, camelCase.all);
  }

  accept(id: Id) {
    return this.http.general.post<TerminationNormalized>(`/cluster_terminations/accept/${id}`, {}, camelCase.all);
  }
  decline(id: Id) {
    return this.http.general.post<TerminationNormalized>(`/cluster_terminations/deny/${id}`, {}, camelCase.all);
  }

  constructor(private http: HttpService, private store: Store<fromRoot.State>) {}
}
