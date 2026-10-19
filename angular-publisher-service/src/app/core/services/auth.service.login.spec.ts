import { PLATFORM_ID } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { ApiService } from './api.service';
import { AuthService } from './auth.service';

describe('AuthService login', () => {
  let api: jasmine.SpyObj<ApiService>;

  beforeEach(() => {
    api = jasmine.createSpyObj<ApiService>('ApiService', ['post', 'get']);
    TestBed.configureTestingModule({
      providers: [
        AuthService,
        { provide: ApiService, useValue: api },
        { provide: Router, useValue: jasmine.createSpyObj<Router>('Router', ['navigate']) },
        { provide: PLATFORM_ID, useValue: 'browser' }
      ]
    });
    localStorage.removeItem('admin_access_token');
  });

  afterEach(() => localStorage.removeItem('admin_access_token'));

  it('stores the access token returned by the login API', async () => {
    const token = { accessToken: 'test-only-token', tokenType: 'Bearer', expiresAt: '2030-01-01T00:00:00Z', adminId: 1 };
    api.post.and.returnValue(Promise.resolve({ data: { data: token } } as any));

    await expectAsync(TestBed.inject(AuthService).login({ username: 'admin', password: 'secret' }))
      .toBeResolvedTo(token);

    expect(localStorage.getItem('admin_access_token')).toBe('test-only-token');
  });

  it('does not access browser storage when running on the server', async () => {
    const setItem = spyOn(localStorage, 'setItem').and.callThrough();
    api.post.and.returnValue(Promise.resolve({
      data: { data: { accessToken: 'test-only-token', tokenType: 'Bearer', expiresAt: '2030-01-01T00:00:00Z', adminId: 1 } }
    } as any));
    TestBed.resetTestingModule();
    TestBed.configureTestingModule({
      providers: [
        AuthService,
        { provide: ApiService, useValue: api },
        { provide: Router, useValue: jasmine.createSpyObj<Router>('Router', ['navigate']) },
        { provide: PLATFORM_ID, useValue: 'server' }
      ]
    });

    await TestBed.inject(AuthService).login({ username: 'admin', password: 'secret' });

    expect(setItem).not.toHaveBeenCalled();
  });
});
