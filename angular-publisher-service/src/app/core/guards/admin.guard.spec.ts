import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { UrlTree } from '@angular/router';
import { adminGuard } from './admin.guard';
import { AuthService } from '../services/auth.service';

describe('adminGuard', () => {
  it('redirects unauthenticated navigation to login', () => {
    const router = jasmine.createSpyObj<Router>('Router', ['createUrlTree']);
    TestBed.configureTestingModule({ providers: [
      { provide: AuthService, useValue: { isAuthenticated: () => false } },
      { provide: Router, useValue: router }
    ] });
    const tree = {} as UrlTree;
    router.createUrlTree.and.returnValue(tree);
    expect(TestBed.runInInjectionContext(() => adminGuard({} as any, { url: '/admin' } as any))).toBe(tree as any);
    expect(router.createUrlTree).toHaveBeenCalled();
  });
});