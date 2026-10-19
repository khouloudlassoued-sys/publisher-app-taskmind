import { PLATFORM_ID } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import axios from 'axios';
import { LoaderService } from './loader.service';
import { ApiService } from './api.service';

describe('ApiService authentication interceptors', () => {
  let requestSuccess: (config: any) => any;
  let responseFailure: (error: any) => Promise<never>;
  let router: jasmine.SpyObj<Router>;
  let loader: jasmine.SpyObj<LoaderService>;

  beforeEach(() => {
    const requestUse = jasmine.createSpy('request.use');
    const responseUse = jasmine.createSpy('response.use');
    const axiosInstance = { interceptors: { request: { use: requestUse }, response: { use: responseUse } } };
    spyOn(axios, 'create').and.returnValue(axiosInstance as any);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    Object.assign(router, { url: '/admin' });
    loader = jasmine.createSpyObj<LoaderService>('LoaderService', ['start', 'stop']);
    TestBed.configureTestingModule({
      providers: [
        ApiService,
        { provide: LoaderService, useValue: loader },
        { provide: Router, useValue: router },
        { provide: PLATFORM_ID, useValue: 'browser' }
      ]
    });

    TestBed.inject(ApiService);
    requestSuccess = requestUse.calls.mostRecent().args[0];
    responseFailure = responseUse.calls.mostRecent().args[1];
    localStorage.removeItem('admin_access_token');
  });

  afterEach(() => localStorage.removeItem('admin_access_token'));

  it('adds the stored bearer token to non-login requests', () => {
    localStorage.setItem('admin_access_token', 'test-only-token');
    const config = { url: '/auth/me', headers: {} };

    expect(requestSuccess(config).headers.Authorization).toBe('Bearer test-only-token');
  });

  it('clears the token and redirects to login after an unauthorized response', async () => {
    localStorage.setItem('admin_access_token', 'test-only-token');

    await expectAsync(responseFailure({ response: { status: 401 } })).toBeRejected();

    expect(localStorage.getItem('admin_access_token')).toBeNull();
    expect(router.navigate).toHaveBeenCalledWith(['/admin/login'], {
      queryParams: { returnUrl: '/admin' }
    });
    expect(loader.stop).toHaveBeenCalled();
  });
});
