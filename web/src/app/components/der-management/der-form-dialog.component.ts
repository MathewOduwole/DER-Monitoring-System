import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';

import { DER } from '../../models/der.model';

interface DialogData {
  mode: 'create' | 'edit';
  der?: DER;
}

@Component({
  selector: 'app-der-form-dialog',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatDialogModule, MatFormFieldModule, MatInputModule,
    MatSelectModule, MatButtonModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ data.mode === 'create' ? 'Register New DER' : 'Edit DER' }}</h2>
    <mat-dialog-content>
      <form class="form-grid">
        <mat-form-field appearance="outline">
          <mat-label>Name</mat-label>
          <input matInput [(ngModel)]="form.name" name="name"
                 [disabled]="data.mode === 'edit'" required>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>MRID ID</mat-label>
          <input matInput [(ngModel)]="form.mrid_id" name="mrid_id" required>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Type</mat-label>
          <mat-select [(ngModel)]="form.type" name="type" required>
            <mat-option value="solar">Solar</mat-option>
            <mat-option value="wind">Wind</mat-option>
            <mat-option value="battery">Battery</mat-option>
            <mat-option value="generator">Generator</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Location</mat-label>
          <input matInput [(ngModel)]="form.location" name="location">
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-raised-button color="primary" (click)="submit()"
              [disabled]="!isValid()">
        {{ data.mode === 'create' ? 'Register' : 'Save' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .form-grid {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 360px;
    }
  `],
})
export class DerFormDialogComponent {
  form = {
    name: '',
    mrid_id: '',
    type: '',
    location: '',
  };

  constructor(
    public dialogRef: MatDialogRef<DerFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData,
  ) {
    if (data.der) {
      this.form = {
        name: data.der.name,
        mrid_id: data.der.mrid_id,
        type: data.der.type,
        location: data.der.location || '',
      };
    }
  }

  isValid(): boolean {
    return !!this.form.name && !!this.form.mrid_id && !!this.form.type;
  }

  submit(): void {
    if (this.isValid()) {
      this.dialogRef.close(this.form);
    }
  }
}
