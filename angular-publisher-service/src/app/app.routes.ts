import { Routes } from '@angular/router';
import { BooksComponent } from './features/books/books.component';
import { MagazinesComponent } from './features/magazines/magazines.component';
import { AuthorsComponent } from './features/authors/authors.component';
import { PublicationsComponent } from './features/publications/publications.component';
import { LoginComponent } from './features/admin/login.component';
import { DashboardComponent } from './features/admin/dashboard.component';
import { adminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  { path: 'admin/login', component: LoginComponent },
  { path: 'admin', component: DashboardComponent, canActivate: [adminGuard] },
  { path: 'books', component: BooksComponent },
  { path: 'magazines', component: MagazinesComponent },
  { path: 'authors', component: AuthorsComponent },
  { path: 'publications', component: PublicationsComponent },
  { path: '', redirectTo: 'books', pathMatch: 'full' },
];
