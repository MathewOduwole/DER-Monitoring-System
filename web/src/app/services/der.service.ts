import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { DER, CreateDERRequest, UpdateDERRequest } from '../models/der.model';
import { TelemetryReading } from '../models/telemetry.model';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class DerService {
  private readonly baseUrl = `${environment.apiUrl}/api/ders`;

  constructor(private http: HttpClient) {}

  list(): Observable<DER[]> {
    return this.http.get<DER[]>(this.baseUrl);
  }

  register(data: CreateDERRequest): Observable<DER> {
    return this.http.post<DER>(this.baseUrl, data);
  }

  update(derName: string, data: UpdateDERRequest): Observable<DER> {
    return this.http.put<DER>(`${this.baseUrl}/${derName}`, data);
  }

  delete(derName: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/${derName}`);
  }

  getTimeSeriesData(derName: string, start?: string, end?: string): Observable<TelemetryReading[]> {
    let url = `${this.baseUrl}/${derName}/data`;
    const params: string[] = [];
    if (start) params.push(`start=${encodeURIComponent(start)}`);
    if (end) params.push(`end=${encodeURIComponent(end)}`);
    if (params.length) url += `?${params.join('&')}`;
    return this.http.get<TelemetryReading[]>(url);
  }
}
