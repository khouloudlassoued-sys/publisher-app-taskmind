import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { LoginComponent } from './login.component';
import { AuthService } from '../../core/services/auth.service';

describe('LoginComponent', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let auth: jasmine.SpyObj<AuthService>;

  beforeEach(async () => {
    auth = jasmine.createSpyObj('AuthService', ['login']);
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        { provide: AuthService, useValue: auth },
        { provide: Router, useValue: jasmine.createSpyObj('Router', ['navigateByUrl']) },
        { provide: ActivatedRoute, useValue: { snapshot: { queryParamMap: { get: () => null } } } }
      ]
    }).compileComponents();
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
  });

  it('rejects an incomplete login form', () => {
    component.submit();
    expect(component.errorMessage).toBe('Username and password are required.');
    expect(auth.login).not.toHaveBeenCalled();
  });

  it('shows a generic error for invalid credentials', async () => {
    component.username = 'admin'; component.password = 'wrong';
    auth.login.and.returnValue(Promise.reject(new Error('denied')));
    component.submit();
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(component.errorMessage).toBe('Invalid username or password.');
  });

});