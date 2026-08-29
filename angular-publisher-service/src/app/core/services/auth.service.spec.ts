import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { ApiService } from './api.service';

describe('AuthService', () => {
  it('clears the browser token on logout', () => {
    TestBed.configureTestingModule({ providers: [
      AuthService,
      { provide: ApiService, useValue: {} },
      { provide: Router, useValue: jasmine.createSpyObj('Router', ['navigate']) }
    ] });
    localStorage.setItem('admin_access_token', 'token');
    TestBed.inject(AuthService).logout();
    expect(localStorage.getItem('admin_access_token')).toBeNull();
  });
});