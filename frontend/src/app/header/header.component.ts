import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UserService } from '../services/user.service';
import { UserStateService } from '../services/user-state.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent implements OnInit  {
  currentUserId: string | null = "";
  currentUserName: string | null = "";

  constructor(private userStateService: UserStateService) {}

  ngOnInit() {
    this.userStateService.getCurrentUser().subscribe(user => {
      this.currentUserId = user.id;
      this.currentUserName = user.name;
    });
  }
}

