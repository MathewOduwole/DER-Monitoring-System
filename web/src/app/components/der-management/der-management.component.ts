import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subject, takeUntil } from 'rxjs';

import { DER, CreateDERRequest } from '../../models/der.model';
import { DerService } from '../../services/der.service';
import { DerFormDialogComponent } from './der-form-dialog.component';

@Component({
  selector: 'app-der-management',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatCardModule, MatTableModule, MatButtonModule, MatIconModule,
    MatDialogModule, MatFormFieldModule, MatInputModule, MatSelectModule,
    MatSnackBarModule, MatProgressSpinnerModule,
  ],
  template: `
    <div class="der-management">
      <div class="header">
        <div>
          <h1>DER Management</h1>
          <p class="subtitle">Register, update, and remove Distributed Energy Resources</p>
        </div>
        <button mat-raised-button color="primary" (click)="openCreateDialog()">
          <mat-icon>add</mat-icon> Register DER
        </button>
      </div>

      @if (loading) {
        <div class="spinner-container">
          <mat-spinner diameter="48"></mat-spinner>
        </div>
      }

      @if (!loading && ders.length === 0) {
        <mat-card class="empty-state">
          <mat-card-content>
            <mat-icon class="empty-icon">electrical_services</mat-icon>
            <h3>No DERs registered</h3>
            <p>Click "Register DER" above to add your first resource.</p>
          </mat-card-content>
        </mat-card>
      }

      @if (!loading && ders.length > 0) {
        <mat-card>
          <table mat-table [dataSource]="ders" class="full-width">
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Name</th>
              <td mat-cell *matCellDef="let der">{{ der.name }}</td>
            </ng-container>

            <ng-container matColumnDef="mrid_id">
              <th mat-header-cell *matHeaderCellDef>MRID</th>
              <td mat-cell *matCellDef="let der">{{ der.mrid_id }}</td>
            </ng-container>

            <ng-container matColumnDef="type">
              <th mat-header-cell *matHeaderCellDef>Type</th>
              <td mat-cell *matCellDef="let der" class="type-cell">
                <mat-icon class="type-icon">{{ getTypeIcon(der.type) }}</mat-icon>
                {{ der.type }}
              </td>
            </ng-container>

            <ng-container matColumnDef="location">
              <th mat-header-cell *matHeaderCellDef>Location</th>
              <td mat-cell *matCellDef="let der">{{ der.location || '-' }}</td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let der">
                <button mat-icon-button color="primary" (click)="openEditDialog(der)" matTooltip="Edit">
                  <mat-icon>edit</mat-icon>
                </button>
                <button mat-icon-button color="warn" (click)="deleteDer(der)" matTooltip="Delete">
                  <mat-icon>delete</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </mat-card>
      }
    </div>
  `,
  styles: [`
    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
    }
    .subtitle { color: #666; }
    .spinner-container { display: flex; justify-content: center; padding: 48px; }
    .full-width { width: 100%; }
    .empty-state { text-align: center; padding: 48px; }
    .empty-icon { font-size: 64px; height: 64px; width: 64px; color: #ccc; }
    .type-cell { display: flex; align-items: center; gap: 8px; }
    .type-icon { font-size: 18px; height: 18px; width: 18px; color: #1976d2; }
  `],
})
export class DerManagementComponent implements OnInit, OnDestroy {
  ders: DER[] = [];
  loading = true;
  displayedColumns = ['name', 'mrid_id', 'type', 'location', 'actions'];

  private destroy$ = new Subject<void>();

  constructor(
    private derService: DerService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadDers();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getTypeIcon(type: string): string {
    const icons: Record<string, string> = {
      solar: 'wb_sunny',
      wind: 'air',
      battery: 'battery_charging_full',
    };
    return icons[type] || 'electrical_services';
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(DerFormDialogComponent, {
      width: '480px',
      data: { mode: 'create' },
    });

    dialogRef.afterClosed().subscribe((result: CreateDERRequest | undefined) => {
      if (result) {
        this.derService.register(result)
          .pipe(takeUntil(this.destroy$))
          .subscribe({
            next: () => {
              this.snackBar.open('DER registered successfully', 'Close', { duration: 3000 });
              this.loadDers();
            },
            error: (err) => {
              const msg = err.error?.error || 'Failed to register DER';
              this.snackBar.open(msg, 'Close', { duration: 5000 });
            },
          });
      }
    });
  }

  openEditDialog(der: DER): void {
    const dialogRef = this.dialog.open(DerFormDialogComponent, {
      width: '480px',
      data: { mode: 'edit', der },
    });

    dialogRef.afterClosed().subscribe((result: CreateDERRequest | undefined) => {
      if (result) {
        this.derService.update(der.name, result)
          .pipe(takeUntil(this.destroy$))
          .subscribe({
            next: () => {
              this.snackBar.open('DER updated successfully', 'Close', { duration: 3000 });
              this.loadDers();
            },
            error: () => {
              this.snackBar.open('Failed to update DER', 'Close', { duration: 5000 });
            },
          });
      }
    });
  }

  deleteDer(der: DER): void {
    if (!confirm(`Delete "${der.name}"? This will also remove all its telemetry data.`)) {
      return;
    }

    this.derService.delete(der.name)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.snackBar.open('DER deleted', 'Close', { duration: 3000 });
          this.loadDers();
        },
        error: () => {
          this.snackBar.open('Failed to delete DER', 'Close', { duration: 5000 });
        },
      });
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
