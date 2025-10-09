import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../services/user.service';
import { Subscriber } from '../models/user.interface';
import { CommonModule } from '@angular/common';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-subscriptions-page',
  templateUrl: './subscriptions-page.component.html',
  styleUrl: './subscriptions-page.component.css',
  imports: [CommonModule]
})
export class SubscriptionsPageComponent implements OnInit {
  subscriptions: Subscriber[] = [];
  userId: string = '';
  loading = true;
  error = false;

  constructor(
    private route: ActivatedRoute, 
    private userService: UserService,
    private navigateToService: NavigateService, 
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.userId = params['id'];
      this.userService.getSubscriptions(this.userId).subscribe({
      next: data => {
        this.subscriptions = data;
        this.loading = false;
      },
      error: err => {
        this.error = true;
        this.loading = false;
      }
    });
    });
  }

  navigateToProfile(id: string) {
    this.navigateToService.navigateToProfile(id);
  }
}
