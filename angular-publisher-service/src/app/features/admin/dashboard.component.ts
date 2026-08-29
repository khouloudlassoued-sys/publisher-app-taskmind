import { Component } from '@angular/core';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent {
  constructor(private auth: AuthService) {}
  logout(): void { this.auth.logout(); }
}