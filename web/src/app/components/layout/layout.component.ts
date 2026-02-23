import { Component } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [
    RouterOutlet, RouterLink, RouterLinkActive,
    MatToolbarModule, MatSidenavModule, MatListModule,
    MatIconModule, MatButtonModule,
  ],
  template: `
    <div class="layout-container">
      <mat-toolbar color="primary" class="toolbar">
        <button mat-icon-button (click)="sidenav.toggle()">
          <mat-icon>menu</mat-icon>
        </button>
        <span class="toolbar-title">DER Monitoring System</span>
      </mat-toolbar>

      <mat-sidenav-container class="sidenav-container">
        <mat-sidenav #sidenav mode="side" opened class="sidenav">
          <mat-nav-list>
            <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
              <mat-icon matListItemIcon>dashboard</mat-icon>
              <span matListItemTitle>Dashboard</span>
            </a>
            <a mat-list-item routerLink="/ders" routerLinkActive="active-link">
              <mat-icon matListItemIcon>electrical_services</mat-icon>
              <span matListItemTitle>DER Management</span>
            </a>
            <a mat-list-item routerLink="/charts" routerLinkActive="active-link">
              <mat-icon matListItemIcon>bar_chart</mat-icon>
              <span matListItemTitle>Charts</span>
            </a>
          </mat-nav-list>
        </mat-sidenav>

        <mat-sidenav-content class="content">
          <router-outlet />
        </mat-sidenav-content>
      </mat-sidenav-container>
    </div>
  `,
  styles: [`
    .layout-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .toolbar {
      position: sticky;
      top: 0;
      z-index: 1000;
    }
    .toolbar-title {
      margin-left: 12px;
      font-size: 1.1rem;
      font-weight: 500;
    }
    .sidenav-container {
      flex: 1;
    }
    .sidenav {
      width: 240px;
    }
    .content {
      padding: 24px;
      background-color: #fafafa;
    }
    .active-link {
      background-color: rgba(0, 0, 0, 0.04);
    }
  `],
})
export class LayoutComponent {}
