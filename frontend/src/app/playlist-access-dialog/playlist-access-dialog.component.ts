import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PlaylistService } from '../services/playlist.service';
import { UserService } from '../services/user.service';
import { FormsModule } from '@angular/forms';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-playlist-access-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './playlist-access-dialog.component.html',
  styleUrl: './playlist-access-dialog.component.css'
})
export class PlaylistAccessDialogComponent implements OnInit {
  @Input() playlistId!: string;
  @Output() close = new EventEmitter<void>();
  @Output() nameChange = new EventEmitter<string>();
  @Output() descriptionChange = new EventEmitter<string>();

  playlist: any = null;
  loading = true;
  errorMsg = '';
  publicity: boolean = false;
  name: string = '';
  description: string = '';
  publicityLoading = false;
  creator: any = null;
  collaborators: any[] = [];
  editCollaborators = false;
  addCollaborators = false;
  searchQuery = '';
  searchResults: any[] = [];
  searchLoading = false;
  searchError = '';

  constructor(
    private playlistService: PlaylistService, 
    private userService: UserService,
    private navigateToService: NavigateService
  ) {}

  ngOnInit() {
    this.fetchPlaylist();
  }

  fetchPlaylist() {
    this.loading = true;
    this.playlistService.getPlaylistDetails(this.playlistId).subscribe({
      next: (data) => {
        this.playlist = Array.isArray(data) ? data[0] : data;
        this.publicity = this.playlist.is_public;
        this.name = this.playlist.name;
        this.description = this.playlist.description;
        this.fetchCreator();
        this.fetchCollaborators();
        this.loading = false;
      },
      error: () => {
        this.errorMsg = 'Ошибка загрузки данных плейлиста';
        this.loading = false;
      }
    });
  }

  fetchCreator() {
    if (!this.playlist?.userid) return;
    this.userService.getUserById(this.playlist.userid).subscribe({
      next: (user) => this.creator = user,
      error: () => this.creator = null
    });
  }

  fetchCollaborators() {
    if (!this.playlist?.collaborators) return;
    this.collaborators = [];
    this.playlist.collaborators.forEach((userid: string) => {
      this.userService.getUserById(userid).subscribe({
        next: (user) => {
          this.collaborators.push(user);
        }
      });
    });
    }

  setPublicity(publicity: boolean) {
    if (this.publicityLoading || this.publicity === publicity) return;
    this.publicityLoading = true;
    this.playlistService.setPlaylistPublicity(this.playlistId, publicity).subscribe({
      next: () => {
        this.publicity = publicity;
        this.publicityLoading = false;
      },
      error: () => {
        this.errorMsg = 'Ошибка смены публичности';
        this.publicityLoading = false;
      }
    });
  }

  setName() {
    this.playlistService.setPlaylistName(this.playlistId, this.name).subscribe({
      next: () => {
        this.nameChange.emit(this.name);
      },
      error: () => {
        this.errorMsg = 'Ошибка смены имени';
      }
    });
  }

  setDescription() {
    this.playlistService.setPlaylistDescription(this.playlistId, this.description).subscribe({
      next: () => {
        this.descriptionChange.emit(this.description);
      },
      error: () => {
        this.errorMsg = 'Ошибка смены описания';
      }
    });
  }

  startEditCollaborators() {
    this.editCollaborators = true;
  }
  finishEditCollaborators() {
    this.editCollaborators = false;
  }

  removeCollaborator(user: any) {
    this.playlistService.removeCollaborator(this.playlistId, user.userid).subscribe({
      next: () => {
        this.collaborators = this.collaborators.filter(c => c.userid !== user.userid);
      },
      error: () => {
        this.errorMsg = 'Ошибка удаления коллаборатора';
      }
    });
  }

  startAddCollaborators() {
    this.addCollaborators = true;
    this.searchQuery = '';
    this.searchResults = [];
    this.searchError = '';
  }
  cancelAddCollaborators() {
    this.addCollaborators = false;
    this.searchQuery = '';
    this.searchResults = [];
    this.searchError = '';
  }
  
  searchUsers() {
    if (!this.searchQuery.trim()) return;
    this.searchLoading = true;
    this.searchError = '';
    
    this.userService.searchUsers(this.searchQuery).subscribe({
      next: (users) => {
        // Собираем ID для исключения
        const excludedIds = [
          this.creator?.userid, 
          ...(this.collaborators?.map(c => c.userid) || [])
        ].filter(Boolean);
  
        // Фильтруем результаты
        this.searchResults = users.filter(user => 
          !excludedIds.includes(user.userid)
        );
        
        this.searchLoading = false;
      },
      error: () => {
        this.searchError = 'Ошибка поиска пользователей';
        this.searchLoading = false;
      }
    });
  }

  addCollaborator(user: any) {
    this.playlistService.addCollaborator(this.playlistId, user.userid).subscribe({
      next: () => {
        this.collaborators.push(user);
        this.searchResults = this.searchResults.filter(u => u.userid !== user.userid);
      },
      error: () => {
        this.errorMsg = 'Ошибка добавления коллаборатора';
      }
    });
  }
  closeDialog() {
    this.close.emit();
  }

  navigateToProfile(userId: string) {
    this.navigateToService.navigateToProfileInNewWindow(userId);
  }
} 