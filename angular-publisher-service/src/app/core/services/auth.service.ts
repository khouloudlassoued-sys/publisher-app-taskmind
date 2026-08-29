import { Inject, Injectable, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from './api.service';
import { AdminProfile, ApiResponse, AuthToken, AuthenticationRequest } from '../models/auth.model';

const TOKEN_KEY = 'admin_access_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  constructor(private api: ApiService, private router: Router, @Inject(PLATFORM_ID) private platformId: object) {}

  isAuthenticated(): boolean {
    return isPlatformBrowser(this.platformId) && !!localStorage.getItem(TOKEN_KEY);
  }

  login(credentials: AuthenticationRequest): Promise<AuthToken> {
    return this.api.post<ApiResponse<AuthToken>>('/api/v1/auth/login', credentials).then(response => {
      if (isPlatformBrowser(this.platformId)) localStorage.setItem(TOKEN_KEY, response.data.data.accessToken);
      return response.data.data;
    });
  }

  me(): Promise<AdminProfile> {
    return this.api.get<ApiResponse<AdminProfile>>('/api/v1/auth/me').then(response => response.data.data);
  }

  logout(): void {
    if (isPlatformBrowser(this.platformId)) localStorage.removeItem(TOKEN_KEY);
    void this.router.navigate(['/admin/login']);
  }
}