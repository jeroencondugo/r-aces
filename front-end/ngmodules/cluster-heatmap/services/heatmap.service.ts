import { Injectable } from '@angular/core';
import { Id } from '@shared/models/id.model';
import { Observable } from 'rxjs';
import { camelCase, HttpService } from '@core/services/http.service';
import { HttpParams } from '@angular/common/http';
import { HeatmapChart, HeatmapConfig, HeatmapPayload } from '../models/heatmap.model';
import { toDate, toShortISO } from '@shared/utils/date.utils';
import { toDict } from '@shared/utils/common.utils';
import { map } from 'rxjs/operators';
import { PruneOut } from '@shared/types/prune-out.type';

type HeatmapConfigDTO = PruneOut<HeatmapConfig, 'measure'>;

@Injectable()
export class HeatmapService {
  loadData(payload: HeatmapPayload) {
    const measure = `${payload.measure}`;
    const excess = (payload.excess ?? []).toString();
    const demand = (payload.demand ?? []).toString();

    const { resolution, period, startDate: startDateFullIso } = payload;
    const startDate = toShortISO(toDate(startDateFullIso));

    const params = new HttpParams({
      fromObject: {
        startDate,
        resolution: resolution.toLowerCase(),
        period: period.toLowerCase(),
        measure,
        ...(!!excess && { excess }),
        ...(!!demand && { demand }),
      },
    });

    return this._http
      .get<readonly HeatmapChart[]>('/meters/heatmap', { params })
      .pipe(map((heatmaps) => toDict(heatmaps)));
  }

  loadConfig(measureId: Id): Observable<HeatmapConfig> {
    const measure = `${measureId}`;
    const params = new HttpParams({ fromObject: { measure } });

    return this._http
      .get<HeatmapConfigDTO>('/meters/heatmap/config', { params, ...camelCase.response })
      .pipe(map((config) => ({ measure: measureId, ...config })));
  }

  constructor(private _http: HttpService) {}
}
