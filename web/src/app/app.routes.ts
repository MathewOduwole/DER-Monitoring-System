import { Routes } from '@angular/router';
import { LayoutComponent } from './components/layout/layout.component';

export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent),
      },
      {
        path: 'ders',
        loadComponent: () =>
          import('./components/der-management/der-management.component').then(m => m.DerManagementComponent),
      },
      {
        path: 'charts',
        loadComponent: () =>
          import('./components/chart-view/chart-view.component').then(m => m.ChartViewComponent),
      },
    ],
  },
];
