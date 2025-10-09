import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService} from '../services/user.service';
import { UserProfile, UserShort, Subscriber  } from '../models/user.interface';
import { PlaylistService } from '../services/playlist.service';
import { Playlist } from '../models/playlists.interface';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GradientService } from '../services/gradient.service';
import { NavigateService } from '../services/navigateTo.service';
import { UpdateUserProfileDialogComponent } from '../update-user-profile-dialog/update-user-profile-dialog.component';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-profile-page',
  templateUrl: './profile-page.component.html',
  styleUrls: ['./profile-page.component.css'],
  standalone: true,
  imports: [CommonModule, FormsModule, UpdateUserProfileDialogComponent] 
})
export class ProfilePageComponent implements OnInit {
  profile: UserProfile | null = null;
  currentUser: UserShort | null = null;
  isOwnProfile = false;
  isSubscribed = false;
  subscribers: Subscriber[] = [];
  subscriptions: Subscriber[] = [];
  playlists: Playlist[] = [];
  userId: string | null = '';
  showSubscribeBtn = false;
  playlistGradients: string[] = [];
  searchQuery: string = '';
  searchResults: UserProfile[] = [];
  searchLoading: boolean = false;
  searchError: string = '';
  dialogOpen = false;

  constructor(
    private route: ActivatedRoute,
    private userService: UserService,
    private authService: AuthService, 
    private playlistService: PlaylistService,
    private gradientService: GradientService,
    private navigateToService: NavigateService, 
    private router: Router
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      this.userId = id;
      if (!id) return;
      this.userService.getCurrentUser().subscribe(current => {
        this.currentUser = current;
        this.isOwnProfile = current.userid === id;
        this.loadProfile(id);
      });
    });
  }

  loadProfile(id: string) {
    this.userService.getUserById(id).subscribe(profile => {
      this.profile = profile;
      this.loadSubscribers(id);
      this.loadPlaylists(id);
    });
  }

  loadSubscribers(id: string) {
    this.userService.getSubscribers(id).subscribe({
      next: (subs) => {
        this.subscribers = subs;
        if (this.currentUser && !this.isOwnProfile) {
          this.isSubscribed = subs.some(s => s.userid === this.currentUser!.userid);
          this.showSubscribeBtn = true;
        } else {
          this.showSubscribeBtn = false;
          this.isSubscribed = false;
        }
      },
      error: () => {
        this.subscribers = [];
        this.isSubscribed = false;
        this.showSubscribeBtn = this.currentUser !== null && !this.isOwnProfile;
      }
    });
  }
  
  loadPlaylists(id: string) {
    this.playlistService.getPlaylistsForTargetUser(id).subscribe({
      next: (playlists) => {
        this.playlists = playlists.filter(
          p => p.userid === id && p.is_public
        );
        this.playlistGradients = this.playlists.map(() => this.gradientService.getRandomGradient());
      },
      error: (err) => {
        this.playlists = [];
        this.playlistGradients = [];
      }
    });
  }

  searchUsers() {
    if (!this.searchQuery.trim()) return;
    this.searchLoading = true;
    this.searchError = '';
    this.userService.searchUsers(this.searchQuery).subscribe({
      next: (users) => {
        this.searchResults = users;
        this.searchLoading = false;
      },
      error: () => {
        this.searchError = 'Ошибка поиска пользователей';
        this.searchLoading = false;
      }
    });
  }

  clearSearch() {
    this.searchQuery = '';
    this.searchResults = [];
    this.searchError = '';
  }

  onSubscribe(userid: string) {
    this.userService.subscribe(userid).subscribe(() => {
      this.isSubscribed = true;
      this.loadProfile(userid);
    });
  }

  onUnsubscribe(userid: string) {
    this.userService.unsubscribe(userid).subscribe(() => {
      this.isSubscribed = false;
      this.loadProfile(userid);
    });
  }

  navigateToProfile(userid: string) {
    this.navigateToService.navigateToProfile(userid);
  }

  navigateToSubscribers(userid: string) {
    this.navigateToService.navigateToSubscribers(userid);
  }

  navigateToSubscriptions(userid: string) {
    this.navigateToService.navigateToSubscriptions(userid);
  }

  navigateToPlaylist(playlistId: string) {
    this.navigateToService.navigateToPlaylist(playlistId)
  }

  openEditProfileDialog() {
    this.dialogOpen = true;
  }

  onDialogClose(updated: boolean) {
    this.dialogOpen = false;
    if (updated && this.userId) {
      this.loadProfile(this.userId);
    }
  }

  logout() {
    this.authService.removeToken();
    localStorage.removeItem('currentUserID');
    localStorage.removeItem('currentUserName');
    this.navigateToService.navigateToLogin();
  }

  isAuthenticated() {
    return this.authService.isAuthenticated();
  }
}