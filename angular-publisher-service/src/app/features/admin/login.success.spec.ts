import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { LoginComponent } from './login.component';
import { AuthService } from '../../core/services/auth.service';

describe('LoginComponent successful login', () => {
  let component: LoginComponent;
  let auth: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let fixture: ComponentFixture<LoginComponent>;

  beforeEach(async () => {
    auth = jasmine.createSpyObj<AuthService>('AuthService', ['login']);
    router = jasmine.createSpyObj<Router>('Router', ['navigateByUrl']);
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        { provide: AuthService, useValue: auth },
        { provide: Router, useValue: router },
        { provide: ActivatedRoute, useValue: { snapshot: { queryParamMap: { get: () => '/admin/accounts' } } } }
      ]
    }).compileComponents();
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
  });

  it('redirects to the requested protected URL and clears the submitting state', async () => {
    auth.login.and.returnValue(Promise.resolve({
      accessToken: 'test-only-token', tokenType: 'Bearer', expiresAt: '2030-01-01T00:00:00Z', adminId: 1
    }));
    component.username = 'admin';
    component.password = 'secret';

    component.submit();
    await new Promise<void>(resolve => setTimeout(resolve, 0));

    expect(auth.login).toHaveBeenCalledWith({ username: 'admin', password: 'secret' });
    expect(router.navigateByUrl).toHaveBeenCalledWith('/admin/accounts');
    expect(component.submitting).toBeFalse();
    expect(component.errorMessage).toBe('');
  });
});
