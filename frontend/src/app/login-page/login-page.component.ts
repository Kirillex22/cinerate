import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavigateService } from '../services/navigateTo.service';
import { UserService } from '../services/user.service';
import { UserStateService } from '../services/user-state.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.css']
})
export class LoginPageComponent {
  login = '';
  password = '';
  error = '';
  loading = false;
  currentUserId = ''

  constructor(
    private auth: AuthService,
    private userService: UserService,
    private userStateService: UserStateService,
    private navigateToService: NavigateService) { }

  onLogin() {
    this.error = '';
    this.loading = true;
    this.auth.login(this.login, this.password).subscribe({
      next: (token) => {
        console.log('Шаг 1: Логин успешен, получен токен.', token);
        this.auth.setToken(token.access_token || token); // Убедитесь, что извлекаете токен правильно

        this.userService.getCurrentUser().subscribe({
          next: user => {
            console.log('Шаг 2: Получен текущий пользователь.', user);
            // ПРОВЕРКА: Существует ли user.userid?
            if (!user || !user.userid) {
              console.error('КРИТИЧЕСКАЯ ОШИБКА: Ответ от getCurrentUser() не содержит userid!');
              this.error = 'Ошибка получения данных пользователя.';
              this.loading = false;
              return; // Прерываем выполнение
            }
            this.currentUserId = user.userid;

            this.userService.getUserById(this.currentUserId).subscribe({
              next: userDetails => {
                console.log('Шаг 3: Получены детали пользователя.', userDetails);
                this.userStateService.setCurrentUser(this.currentUserId, userDetails.username);
                console.log('Шаг 4: Пользователь сохранен, вызываю навигацию...');
                this.navigateToService.navigateToPlane();
              },
              error: err => {
                console.error('ОШИБКА на getUserById:', err);
                this.error = 'Не удалось загрузить детали профиля.';
                this.loading = false;
              }
            });
          },
          error: err => {
            console.error('ОШИБКА на getCurrentUser:', err);
            this.error = 'Не удалось получить данные текущего пользователя.';
            this.loading = false;
          }
        });
      },
      error: (err) => {
        console.error('ОШИБКА на auth.login:', err);
        this.error = 'Неверный логин или пароль';
        this.loading = false;
      }
    });
  }

  goToRegister() {
    this.navigateToService.navigateToRegister();
  }
}