import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserProfile, UpdateUserProfileRequest } from '../models/user.interface';
import { UserService } from '../services/user.service';
import { UserStateService } from '../services/user-state.service';

@Component({
  selector: 'app-update-user-profile-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './update-user-profile-dialog.component.html',
  styleUrl: './update-user-profile-dialog.component.css'
})
export class UpdateUserProfileDialogComponent implements OnInit {
  @Input() profile: UserProfile | null = null;
  @Output() close = new EventEmitter<boolean>();

  form: UpdateUserProfileRequest = {
    userid: '',
    username: '',
    bio: '',
    location: '',
    birth_date: '',
    email: '',
    avatar: '',
    status: 1
  };
  loading = false;
  saving = false;
  errorMsg = '';
  publicity = false; // true = публичный, false = приватный
  publicityLoading = false;

  constructor(private userService: UserService,
    private userStateService: UserStateService
  ) {}

  ngOnInit() {
    if (this.profile) {
      this.form = {
        userid: this.profile.userid,
        username: this.profile.username ?? '',
        bio: this.profile.bio ?? '',
        location: this.profile.location ?? '',
        birth_date: this.profile.birth_date || null,
        email: this.profile.email ?? '',
        avatar: this.profile.avatar ?? '',
        status: this.profile.status ?? 2
      };
      this.publicity = (this.form.status === 2);
    }
  }

  save() {
    if (!this.form.userid) return;
    this.saving = true;
    this.errorMsg = '';
    this.userStateService.setCurrentUser(this.form.userid, this.form.username);
    this.userService.updateUserProfile(this.form.userid, this.form).subscribe({
      next: () => {
        this.saving = false;
        this.close.emit(true);
      },
      error: (err) => {
        this.saving = false;
        this.errorMsg = 'Ошибка сохранения изменений';
      }
    });
  }

  closeDialog(updated: boolean) {
    this.close.emit(updated);
  }

  setPublicity(isPublic: boolean) {
    this.publicity = isPublic;
    this.form.status = isPublic ? 2 : 1;
  }
}
