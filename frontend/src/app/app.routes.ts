import { Router, Routes, UrlTree } from '@angular/router';
import { FilmDetailsComponent } from './film-details/film-details.component';
import { PlaylistDetailsComponent } from './playlist-details/playlist-details.component';
import { ViewsPageComponent } from './views-page/views-page.component';
import { SearchPageComponent } from './search-page/search-page.component';
import { PlaylistsPageComponent } from './playlists-page/playlists-page.component';
import { ProfilePageComponent } from './profile-page/profile-page.component';
import { PlanePageComponent } from './plane-page/plane-page.component';
import { SubcribersPageComponent } from './subcribers-page/subcribers-page.component';
import { SubscriptionsPageComponent } from './subscriptions-page/subscriptions-page.component';
import { LoginPageComponent } from './login-page/login-page.component';
import { RegisterPageComponent } from './register-page/register-page.component';
import { AuthService } from './services/auth.service';
import { inject, PLATFORM_ID } from '@angular/core';
import { filter, map, take, tap } from 'rxjs/operators'; // <-- Убедитесь, что filter импортирован
import { isPlatformBrowser } from '@angular/common';

// Асинхронный guard
export const authGuard = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);
  const platform = isPlatformBrowser(platformId) ? 'BROWSER' : 'SERVER';

  console.log(`[authGuard] EXECUTING on ${platform}`);

  if (!isPlatformBrowser(platformId)) {
    console.log('[authGuard] SERVER: Bypassing guard.');
    return true; // На сервере всегда пропускаем
  }

  // В браузере ждем окончательного статуса аутентификации
  return auth.isAuthenticated$.pipe(
    tap(status => console.log(`[authGuard] BROWSER: Got status from isAuthenticated$: ${status}`)),
    filter(isAuthenticated => isAuthenticated !== null), // Ждем, пока значение не станет true или false
    take(1), // Берем первое "окончательное" значение
    map(isAuthenticated => {
      console.log(`[authGuard] BROWSER: Final decision, isAuthenticated: ${isAuthenticated}`);
      if (isAuthenticated) {
        return true; // Доступ разрешен
      } else {
        console.log('[authGuard] BROWSER: Redirecting to /login');
        return router.parseUrl('/login'); // Перенаправляем на логин
      }
    })
  );
};

export const isBrowserGuard = () => {
  return inject(PLATFORM_ID) === 'browser';
};

export const routes: Routes = [
  { path: 'login', component: LoginPageComponent, canActivate: [isBrowserGuard] },
  { path: 'register', component: RegisterPageComponent, canActivate: [isBrowserGuard] },
  {
    path: '',
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: '/plane', pathMatch: 'full' },
      { path: 'plane', component: PlanePageComponent },
      { path: 'playlists', component: PlaylistsPageComponent },
      { path: 'views', component: ViewsPageComponent },
      { path: 'search', component: SearchPageComponent },
      { path: 'profile/:id', component: ProfilePageComponent },
      { path: 'playlist/:id', component: PlaylistDetailsComponent },
      { path: 'film/:id', component: FilmDetailsComponent },
      { path: 'profile/:id/subscriptions', component: SubscriptionsPageComponent },
      { path: 'profile/:id/subscribers', component: SubcribersPageComponent },
    ]
  }
];