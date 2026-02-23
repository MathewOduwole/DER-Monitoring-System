import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatChipsModule } from '@angular/material/chips';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { Subject, takeUntil, forkJoin } from 'rxjs';

import { DER } from '../../models/der.model';
import { Chart, ChartWithData, CreateChartRequest } from '../../models/chart.model';
import { DerService } from '../../services/der.service';
import { ChartService } from '../../services/chart.service';

const CHART_COLORS = ['#1976d2', '#e53935', '#43a047', '#fb8c00', '#8e24aa', '#00acc1'];

@Component({
  selector: 'app-chart-view',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatCardModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatSelectModule,
    MatSnackBarModule, MatProgressSpinnerModule,
    MatExpansionModule, MatChipsModule,
    BaseChartDirective,
  ],
  template: `
    <div class="chart-view">
      <div class="header">
        <div>
          <h1>Charts</h1>
          <p class="subtitle">Create and visualise DER telemetry data</p>
        </div>
      </div>

      <!-- Create Chart Form -->
      <mat-card class="create-card">
        <mat-card-header>
          <mat-card-title>Create New Chart</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="form-row">
            <mat-form-field appearance="outline" class="name-field">
              <mat-label>Chart Name</mat-label>
              <input matInput [(ngModel)]="newChart.name" placeholder="e.g. Solar Output This Week">
            </mat-form-field>

            <mat-form-field appearance="outline" class="der-select">
              <mat-label>Select DERs (max 3)</mat-label>
              <mat-select [(ngModel)]="newChart.der_names" multiple>
                @for (der of availableDers; track der.id) {
                  <mat-option [value]="der.name"
                              [disabled]="newChart.der_names.length >= 3 && !newChart.der_names.includes(der.name)">
                    {{ der.name }}
                  </mat-option>
                }
              </mat-select>
            </mat-form-field>
          </div>

          <div class="form-row">
            <mat-form-field appearance="outline">
              <mat-label>Start Date</mat-label>
              <input matInput type="datetime-local" [(ngModel)]="newChart.start_date">
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>End Date</mat-label>
              <input matInput type="datetime-local" [(ngModel)]="newChart.end_date">
            </mat-form-field>

            <button mat-raised-button color="primary" (click)="createChart()"
                    [disabled]="!isCreateValid()">
              <mat-icon>add_chart</mat-icon> Create Chart
            </button>
          </div>
        </mat-card-content>
      </mat-card>

      @if (loading) {
        <div class="spinner-container">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }

      <!-- Saved Charts -->
      @for (chart of charts; track chart.id) {
        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>{{ chart.name }}</mat-card-title>
            <mat-card-subtitle>
              {{ chart.der_names.join(', ') }}
            </mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            @if (chartDataMap[chart.id]) {
              <div class="chart-tabs">
                @for (metric of metrics; track metric) {
                  <button mat-stroked-button
                          [color]="activeMetric[chart.id] === metric ? 'primary' : ''"
                          (click)="setMetric(chart.id, metric)">
                    {{ metricLabels[metric] }}
                  </button>
                }
              </div>
              <div class="chart-container">
                <canvas baseChart
                  [datasets]="getChartDatasets(chart.id)"
                  [labels]="getChartLabels(chart.id)"
                  [options]="lineChartOptions"
                  [type]="'line'">
                </canvas>
              </div>
            } @else {
              <div class="spinner-container">
                <mat-spinner diameter="32"></mat-spinner>
              </div>
            }
          </mat-card-content>
          <mat-card-actions align="end">
            <button mat-button (click)="loadChartData(chart)">
              <mat-icon>refresh</mat-icon> Refresh
            </button>
            <button mat-button color="warn" (click)="deleteChart(chart)">
              <mat-icon>delete</mat-icon> Delete
            </button>
          </mat-card-actions>
        </mat-card>
      }
    </div>
  `,
  styles: [`
    .chart-view { max-width: 1200px; }
    .header { margin-bottom: 24px; }
    .subtitle { color: #666; }
    .spinner-container { display: flex; justify-content: center; padding: 32px; }

    .create-card { margin-bottom: 24px; }
    .form-row {
      display: flex;
      gap: 16px;
      align-items: flex-start;
      flex-wrap: wrap;
      margin-top: 8px;
    }
    .name-field { flex: 1; min-width: 200px; }
    .der-select { flex: 1; min-width: 240px; }

    .chart-card { margin-bottom: 24px; }
    .chart-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
    }
    .chart-container {
      position: relative;
      height: 320px;
    }
  `],
})
export class ChartViewComponent implements OnInit, OnDestroy {
  availableDers: DER[] = [];
  charts: Chart[] = [];
  chartDataMap: Record<number, ChartWithData> = {};
  activeMetric: Record<number, string> = {};
  loading = true;

  metrics = ['active_power', 'reactive_power', 'voltage'];
  metricLabels: Record<string, string> = {
    active_power: 'Active Power (W)',
    reactive_power: 'Reactive Power (var)',
    voltage: 'Voltage (V)',
  };

  newChart: CreateChartRequest = {
    name: '',
    der_names: [],
    start_date: '',
    end_date: '',
  };

  lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: { maxTicksLimit: 12 },
      },
    },
    plugins: {
      legend: { position: 'top' },
    },
  };

  private destroy$ = new Subject<void>();

  constructor(
    private derService: DerService,
    private chartService: ChartService,
    private snackBar: MatSnackBar,
  ) {
    this.setDefaultDates();
  }

  ngOnInit(): void {
    this.loadInitialData();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  isCreateValid(): boolean {
    return !!this.newChart.name
      && this.newChart.der_names.length > 0
      && this.newChart.der_names.length <= 3
      && !!this.newChart.start_date
      && !!this.newChart.end_date;
  }

  createChart(): void {
    const payload: CreateChartRequest = {
      ...this.newChart,
      start_date: new Date(this.newChart.start_date).toISOString(),
      end_date: new Date(this.newChart.end_date).toISOString(),
    };

    this.chartService.create(payload)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (chart) => {
          this.snackBar.open('Chart created', 'Close', { duration: 3000 });
          this.charts.unshift(chart);
          this.loadChartData(chart);
          this.newChart = { name: '', der_names: [], start_date: '', end_date: '' };
          this.setDefaultDates();
        },
        error: (err) => {
          const msg = err.error?.error || err.error?.errors || 'Failed to create chart';
          this.snackBar.open(String(msg), 'Close', { duration: 5000 });
        },
      });
  }

  deleteChart(chart: Chart): void {
    if (!confirm(`Delete chart "${chart.name}"?`)) return;

    this.chartService.delete(chart.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.charts = this.charts.filter(c => c.id !== chart.id);
          delete this.chartDataMap[chart.id];
          this.snackBar.open('Chart deleted', 'Close', { duration: 3000 });
        },
        error: () => {
          this.snackBar.open('Failed to delete chart', 'Close', { duration: 5000 });
        },
      });
  }

  loadChartData(chart: Chart): void {
    this.chartService.get(chart.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.chartDataMap[chart.id] = data;
          if (!this.activeMetric[chart.id]) {
            this.activeMetric[chart.id] = 'active_power';
          }
        },
      });
  }

  setMetric(chartId: number, metric: string): void {
    this.activeMetric[chartId] = metric;
  }

  getChartLabels(chartId: number): string[] {
    const data = this.chartDataMap[chartId];
    if (!data?.series) return [];

    const firstDer = Object.keys(data.series)[0];
    if (!firstDer) return [];

    return data.series[firstDer].map(r =>
      new Date(r.timestamp).toLocaleString(undefined, {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
      })
    );
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  getChartDatasets(chartId: number): any[] {
    const data = this.chartDataMap[chartId];
    if (!data?.series) return [];

    const metric = this.activeMetric[chartId] || 'active_power';

    return Object.entries(data.series).map(([derName, readings], index) => ({
      data: readings.map(r => r[metric as keyof typeof r] as number),
      label: derName,
      borderColor: CHART_COLORS[index % CHART_COLORS.length],
      backgroundColor: CHART_COLORS[index % CHART_COLORS.length] + '20',
      fill: true,
      tension: 0.3,
      pointRadius: 0,
      borderWidth: 2,
    }));
  }

  private setDefaultDates(): void {
    const now = new Date();
    const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    this.newChart.end_date = this.toLocalDatetimeString(now);
    this.newChart.start_date = this.toLocalDatetimeString(dayAgo);
  }

  private toLocalDatetimeString(d: Date): string {
    const offset = d.getTimezoneOffset();
    const local = new Date(d.getTime() - offset * 60000);
    return local.toISOString().slice(0, 16);
  }

  private loadInitialData(): void {
    forkJoin({
      ders: this.derService.list(),
      charts: this.chartService.list(),
    })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: ({ ders, charts }) => {
          this.availableDers = ders;
          this.charts = charts;
          this.loading = false;
          charts.forEach(c => this.loadChartData(c));
        },
        error: () => {
          this.loading = false;
        },
      });
  }
}
