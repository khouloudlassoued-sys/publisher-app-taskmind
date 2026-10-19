import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { adminGuard } from './admin.guard';
import { AuthService } from '../services/auth.service';

describe('adminGuard authenticated navigation', () => {
  it('allows navigation for an authenticated administrator', () => {
    const router = jasmine.createSpyObj<Router>('Router', ['createUrlTree']);
    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: { isAuthenticated: () => true } },
        { provide: Router, useValue: router }
      ]
    });

    expect(TestBed.runInInjectionContext(() => adminGuard({} as any, { url: '/admin' } as any))).toBeTrue();
    expect(router.createUrlTree).not.toHaveBeenCalled();
  });
});
