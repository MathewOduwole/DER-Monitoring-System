import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { Subject, takeUntil } from 'rxjs';

import { DER } from '../../models/der.model';
import { DerService } from '../../services/der.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, RouterLink,
    MatCardModule, MatIconModule, MatButtonModule,
    MatProgressSpinnerModule, MatChipsModule,
  ],
  template: `
    <div class="dashboard">
      <h1>Dashboard</h1>
      <p class="subtitle">Overview of registered Distributed Energy Resources</p>

      @if (loading) {
        <div class="spinner-container">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }

      @if (!loading && ders.length === 0) {
        <mat-card class="empty-state">
          <mat-card-content>
            <mat-icon class="empty-icon">electrical_services</mat-icon>
            <h3>No DERs registered yet</h3>
            <p>Register your first Distributed Energy Resource to get started.</p>
            <a mat-raised-button color="primary" routerLink="/ders">
              Go to DER Management
            </a>
          </mat-card-content>
        </mat-card>
      }

      @if (!loading && ders.length > 0) {
        <div class="summary-cards">
          <mat-card class="summary-card">
            <mat-card-content>
              <div class="summary-value">{{ ders.length }}</div>
              <div class="summary-label">Total DERs</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="summary-card">
            <mat-card-content>
              <div class="summary-value">{{ getTypeCount('solar') }}</div>
              <div class="summary-label">Solar</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="summary-card">
            <mat-card-content>
              <div class="summary-value">{{ getTypeCount('wind') }}</div>
              <div class="summary-label">Wind</div>
            </mat-card-content>
          </mat-card>
          <mat-card class="summary-card">
            <mat-card-content>
              <div class="summary-value">{{ getTypeCount('battery') }}</div>
              <div class="summary-label">Battery</div>
            </mat-card-content>
          </mat-card>
        </div>

        <h2>Registered DERs</h2>
        <div class="der-grid">
          @for (der of ders; track der.id) {
            <mat-card class="der-card">
              <mat-card-header>
                <mat-icon mat-card-avatar class="der-type-icon">{{ getTypeIcon(der.type) }}</mat-icon>
                <mat-card-title>{{ der.name }}</mat-card-title>
                <mat-card-subtitle>{{ der.mrid_id }}</mat-card-subtitle>
              </mat-card-header>
              <mat-card-content>
                <div class="der-detail">
                  <mat-icon>category</mat-icon>
                  <mat-chip>{{ der.type }}</mat-chip>
                </div>
                @if (der.location) {
                  <div class="der-detail">
                    <mat-icon>location_on</mat-icon>
                    <span>{{ der.location }}</span>
                  </div>
                }
              </mat-card-content>
            </mat-card>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .dashboard { max-width: 1200px; }
    .subtitle { color: #666; margin-bottom: 24px; }
    .spinner-container { display: flex; justify-content: center; padding: 48px; }

    .empty-state {
      text-align: center;
      padding: 48px;
    }
    .empty-icon {
      font-size: 64px;
      height: 64px;
      width: 64px;
      color: #ccc;
    }

    .summary-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }
    .summary-card { text-align: center; }
    .summary-value { font-size: 2rem; font-weight: 700; color: #1976d2; }
    .summary-label { color: #666; font-size: 0.9rem; margin-top: 4px; }

    .der-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }
    .der-card { transition: box-shadow 0.2s; }
    .der-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .der-type-icon {
      background-color: #e3f2fd;
      border-radius: 50%;
      padding: 8px;
      color: #1976d2;
    }
    .der-detail {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
    }
    .der-detail mat-icon { font-size: 18px; height: 18px; width: 18px; color: #888; }
  `],
})
export class DashboardComponent implements OnInit, OnDestroy {
  ders: DER[] = [];
  loading = true;

  private destroy$ = new Subject<void>();

  constructor(private derService: DerService) {}

  ngOnInit(): void {
    this.loadDers();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getTypeCount(type: string): number {
    return this.ders.filter(d => d.type === type).length;
  }

  getTypeIcon(type: string): string {
    const icons: Record<string, string> = {
      solar: 'wb_sunny',
      wind: 'air',
      battery: 'battery_charging_full',
    };
    return icons[type] || 'electrical_services';
  }

  private loadDers(): void {
    this.derService.list()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (ders) => {
          this.ders = ders;
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        },
      });
  }
}
