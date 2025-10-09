import { Injectable, Inject, PLATFORM_ID, isDevMode, Optional } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { BASE_URL } from '../models/config';
import { isPlatformBrowser } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private tokenKey = 'access_token';
  private baseUrl = BASE_URL;

  private isAuthenticatedSubject = new BehaviorSubject<boolean | null>(null);
  public isAuthenticated$: Observable<boolean | null> = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object,
    @Optional() @Inject('REQUEST_COOKIES') private requestCookies: { [key: string]: string }
  ) {
    const platform = isPlatformBrowser(this.platformId) ? 'BROWSER' : 'SERVER';
    console.log(`[AuthService] CONSTRUCTOR on ${platform}`);
    
    // ВЫПОЛНЯЕМ ПРОВЕРКУ СРАЗУ ПРИ СОЗДАНИИ СЕРВИСА
    this.checkAuthStatus();
  }

  // Этот метод теперь вызывается только из конструктора
  private checkAuthStatus(): void {
    const platform = isPlatformBrowser(this.platformId) ? 'BROWSER' : 'SERVER';
    console.log(`[AuthService] checkAuthStatus() on ${platform}`);
    const hasToken = this.hasToken();
    console.log(`[AuthService] hasToken result: ${hasToken}`);
    this.isAuthenticatedSubject.next(hasToken);
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  // ... все остальные методы (login, register, setToken и т.д.) остаются без изменений ...

  login(login: string, password: string): Observable<any> {
    const params = new HttpParams()
      .set('login', login)
      .set('password', password);
    return this.http.post(this.baseUrl + 'auth/token', {}, { params });
  }

  register(login: string, email: string, password: string): Observable<any> {
    return this.http.post(this.baseUrl + 'auth/register', { login, email, password });
  }

  setToken(token: string) {
    if (!isPlatformBrowser(this.platformId)) return;

    localStorage.setItem(this.tokenKey, token);
    console.log(`[AuthService] Saved token to localStorage`);
    this.isAuthenticatedSubject.next(true);
  }

  getToken(): string | null {
    if (isPlatformBrowser(this.platformId)) {
      const token = localStorage.getItem(this.tokenKey);
      console.log(`[AuthService] Read token from localStorage: ${token}`);
      return token;
    } else {
      return this.requestCookies?.[this.tokenKey] || null;
      }
  }

  removeToken() {
    if (!isPlatformBrowser(this.platformId)) return;

    localStorage.removeItem(this.tokenKey);
    console.log(`[AuthService] Token removed from localStorage`);
    this.isAuthenticatedSubject.next(false);
  }

  isAuthenticated(): boolean {
    return this.isAuthenticatedSubject.value === true;
  }
}