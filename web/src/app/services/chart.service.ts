import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Chart, ChartWithData, CreateChartRequest, UpdateChartRequest } from '../models/chart.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChartService {
  private readonly baseUrl = `${environment.apiUrl}/api/charts`;

  constructor(private http: HttpClient) {}

  list(): Observable<Chart[]> {
    return this.http.get<Chart[]>(this.baseUrl);
  }

  create(data: CreateChartRequest): Observable<Chart> {
    return this.http.post<Chart>(this.baseUrl, data);
  }

  get(chartId: number): Observable<ChartWithData> {
    return this.http.get<ChartWithData>(`${this.baseUrl}/${chartId}`);
  }

  update(chartId: number, data: UpdateChartRequest): Observable<Chart> {
    return this.http.put<Chart>(`${this.baseUrl}/${chartId}`, data);
  }

  delete(chartId: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/${chartId}`);
  }
}
