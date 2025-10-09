import { Component } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from './services/user.service';
import { AuthService } from './services/auth.service';
import { filter } from 'rxjs/operators';
import { MatSnackBarModule } from '@angular/material/snack-bar';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, CommonModule, FormsModule, MatSnackBarModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Cinerate';
  showHeader = true;

  constructor(private userService: UserService, private auth: AuthService, private router: Router) {
    this.router.events.pipe(filter(e => e instanceof NavigationEnd)).subscribe((event: any) => {
      const url = event.urlAfterRedirects || event.url;
      this.showHeader = !(url.startsWith('/login') || url.startsWith('/register'));
    });
  }
}
