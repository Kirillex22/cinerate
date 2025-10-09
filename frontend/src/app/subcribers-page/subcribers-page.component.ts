import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../services/user.service';
import { Subscriber } from '../models/user.interface';
import { CommonModule } from '@angular/common';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-subcribers-page',
  templateUrl: './subcribers-page.component.html',
  styleUrl: './subcribers-page.component.css',
  imports: [CommonModule]
})
export class SubcribersPageComponent implements OnInit {
  subscribers: Subscriber[] = [];
  userId: string = '';
  loading = true;
  error = false;

  constructor(
    private route: ActivatedRoute, 
    private userService: UserService,
    private navigateToService: NavigateService, 
    private router: Router) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.userId = params['id'];
      this.loading = true;
      this.error = false;

      this.userService.getSubscribers(this.userId).subscribe({
        next: data => {
          this.subscribers = data;
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