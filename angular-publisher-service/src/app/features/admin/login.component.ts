import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-admin-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.component.html'
})
export class LoginComponent {
  username = '';
  password = '';
  errorMessage = '';
  submitting = false;

  constructor(private auth: AuthService, private router: Router, private route: ActivatedRoute) {}

  submit(): void {
    this.errorMessage = '';
    if (!this.username.trim() || !this.password) {
      this.errorMessage = 'Username and password are required.';
      return;
    }
    this.submitting = true;
    this.auth.login({ username: this.username, password: this.password }).then(() => {
      const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') || '/admin';
      void this.router.navigateByUrl(returnUrl);
    }).catch(() => this.errorMessage = 'Invalid username or password.').finally(() => this.submitting = false);
  }
}