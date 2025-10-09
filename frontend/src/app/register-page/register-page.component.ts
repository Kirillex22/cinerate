import { Component } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './register-page.component.html',
  styleUrls: ['./register-page.component.css']
})
export class RegisterPageComponent {
  login = '';
  email = '';
  password = '';
  confirmPassword = '';
  error = '';
  loading = false;

  constructor(private auth: AuthService, private navigateToService: NavigateService) {}

  onRegister() {
    this.error = '';
    if (this.password !== this.confirmPassword) {
      this.error = 'Пароли не совпадают';
      return;
    }
    this.loading = true;
    this.auth.register(this.login, this.email, this.password).subscribe({
      next: () => {
        this.auth.login(this.login, this.password).subscribe({
          next: (token) => {
            this.navigateToService.navigateToLogin();
          }
        });
      },
      error: (err) => {
        this.error = 'Ошибка регистрации: ' + (err.error || 'Попробуйте другой логин');
        this.loading = false;
      }
    });
  }
} 