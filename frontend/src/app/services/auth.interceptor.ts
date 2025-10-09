import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NavigateService } from './navigateTo.service';
import { HttpRequest, HttpHandlerFn, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<any>,
  next: HttpHandlerFn
): Observable<HttpEvent<any>> => {
  const snackBar = inject(MatSnackBar);
  const navigateToService = inject(NavigateService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        navigateToService.navigateToLogin();
        snackBar.open('Действие токена истекло. Зайдите в аккаунт ещё раз.', 'Закрыть', {
          duration: 5000,
          verticalPosition: 'bottom'
        });
      }
      return throwError(() => error);
    })
  );
};
