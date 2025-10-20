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
    private navigateToService: NavigateService) {}

  onLogin() {
    this.error = '';
    this.loading = true;
    this.auth.login(this.login, this.password).subscribe({
      next: (token) => {
        this.auth.setToken(token);
        this.userService.getCurrentUser().subscribe(user => {
          this.currentUserId = user.userid;
          this.userService.getUserById(this.currentUserId).subscribe(userDetails => {
            this.userStateService.setCurrentUser(this.currentUserId, userDetails.username);
            this.navigateToService.navigateToPlane();
          });
        });
      },
      error: (err) => {
        this.error = 'Неверный логин или пароль';
        this.loading = false;
      }
    });
  }

  goToRegister() {
    this.navigateToService.navigateToRegister();
  }
} 