import { Observable } from 'rxjs';
import { Injectable } from '@angular/core';

import { camelCase, HttpService } from '@core/services/http.service';
import { TimePeriod } from '@shared/models/filters';
import { Dict } from '@shared/utils/common.utils';
import { FilterConfig, FilterConfigResponse } from '../models/filter-config.model';
import { map } from 'rxjs/operators';
import { Id } from '@shared/models/id.model';
import { GraphNodeNormalized } from '../models/graph-node.model';
import { GraphLinkNormalized } from '../models/graph-link.model';
import { HttpParams } from '@angular/common/http';
import { toShortISO } from '@shared/utils/date.utils';

interface ArcSankeyDataDTO {
  data: {
    nodes: GraphNodeNormalized[];
    links: GraphLinkNormalized[];
  };
}

@Injectable()
export class ArcSankeyService {
  loadData(
    siteId: Id,
    selectedDate: Date,
    endPeriodDate: Date,
    period: TimePeriod,
  ): Observable<{ links: GraphLinkNormalized[]; nodes: GraphNodeNormalized[] }> {
    const params = new HttpParams({
      fromObject: {
        site_id: `${siteId}`,
        start_date: toShortISO(selectedDate),
        end_date: toShortISO(endPeriodDate),
        period,
        type: 'arc',
      },
    });

    return this._http
      .get<ArcSankeyDataDTO>(`/sankey`, { params, ...camelCase.response })
      .pipe(map(({ data }) => data));
  }

  loadConfig() {
    return this._http
      .get<Dict<FilterConfigResponse>>(`/sankey/config`, {
        params: new HttpParams({ fromObject: { type: 'arc' } }),
        ...camelCase.response,
      })
      .pipe(map(normalizeFilterData));
  }

  constructor(private _http: HttpService) {}
}

function normalizeFilterData(
  inputData: Dict<FilterConfigResponse>,
): { entities: Dict<FilterConfig>; ids: ReadonlyArray<Id> } {
  const ids = Object.keys(inputData);
  const entities = ids.reduce((agg, id) => ({ ...agg, [id]: { ...inputData[id], id } }), <Dict<FilterConfig>>{});
  return {
    ids,
    entities,
  };
}
