import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { PlaylistService } from '../services/playlist.service';
import { ActivatedRoute, Router } from '@angular/router';
import { map, switchMap, tap } from 'rxjs';
import { PlaylistContentItem } from '../models/playlist-details.interface';
import { NgFor, NgIf } from '@angular/common';
import { PlaylistAccessDialogComponent } from '../playlist-access-dialog/playlist-access-dialog.component';
import { UserService } from '../services/user.service';
import { UserProfile } from '../models/user.interface';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-playlist-details',
  standalone: true,
  imports: [CommonModule, NgFor, NgIf, PlaylistAccessDialogComponent],
  templateUrl: './playlist-details.component.html',
  styleUrl: './playlist-details.component.css'
})

export class PlaylistDetailsComponent implements OnInit {
  playlistId: string = '';
  playlistName: string = '';
  playlistDescription: string = '';
  films: PlaylistContentItem[] = [];
  hoveredFilm: PlaylistContentItem | null = null;
  editMode: boolean = false;
  showAccessDialog = false;
  showButtonDialog = false;
  isError = false;
  isCreator = false;
  playlistCreatorId: string = '';
  currentUserId: string = '';
  collaborators: UserProfile[] = [];
  collaboratorsMap: { [userid: string]: UserProfile } = {};
  filmCreatorsMap: { [userid: string]: UserProfile } = {};


  constructor(
    private playlistService: PlaylistService,
    private userService: UserService,
    private route: ActivatedRoute,
    private navigateToService: NavigateService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadComponent();
  }

  loadComponent(){
    this.route.paramMap.pipe(
      map(params => params.get('id') || ''),
      tap(id => this.playlistId = id),
      switchMap(id => this.playlistService.getPlaylistContent(id))
    ).subscribe({
      next: films => {
        this.films = films;
        this.loadPlaylistDetailsAndUsers();
      },
      error: () => {
        this.loadPlaylistDetailsAndUsers();
        this.isError = true;
      }
    });
    this.userService.getCurrentUser().subscribe(user => {
      this.currentUserId = user.userid;
    });
  }

  loadPlaylistDetailsAndUsers() {
    this.playlistService.getPlaylistDetails(this.playlistId).subscribe(data => {
      const playlist = Array.isArray(data) ? data[0] : data;
      const collaboratorIds: string[] = playlist.collaborators || [];

      this.playlistName = playlist.name;
      this.playlistDescription = playlist.description;
      this.playlistCreatorId = playlist.userid
      this.isCreator = this.currentUserId == this.playlistCreatorId
      if ((collaboratorIds.includes(this.currentUserId)) || (this.isCreator)){
        this.showButtonDialog = true;
      }
      // Получаем инфу о коллабораторах
      this.collaborators = [];
      this.collaboratorsMap = {};
      collaboratorIds.forEach(userid => {
        this.userService.getUserById(userid).subscribe(user => {
          this.collaborators.push(user);
          this.collaboratorsMap[userid] = user;
        });
      });
      // Получаем инфу о добавивших фильмы
      const creatorIds = Array.from(new Set(this.films.map(f => f.item.creatorid)));
      this.filmCreatorsMap = {};
      creatorIds.forEach(userid => {
        if (!userid) return;
        this.userService.getUserById(userid).subscribe(user => {
          this.filmCreatorsMap[userid] = user;
        });
      });
    });
  }

  showFilmInfo(film: PlaylistContentItem) {
    this.hoveredFilm = film;
  }

  hideFilmInfo() {
    this.hoveredFilm = null;
  }

  getSeasonNumber(film: PlaylistContentItem): string {
    return film.preview.filmid.split('-')[1] || '';
  }

  editPlaylist() {
    this.editMode = true;
  }

  finishEdit() {
    this.editMode = false;
  }

  removeFilm(film: PlaylistContentItem) {
    this.playlistService.removeFilmFromPlaylist(this.playlistId, film.preview.filmid).subscribe({
      next: () => {
        this.films = this.films.filter(f => f.preview.filmid !== film.preview.filmid);
      },
      error: (err: any) => {
        alert('Ошибка при удалении фильма');
      }
    });
  }

  deletePlaylist(){
    this.playlistService.removePlaylist(this.playlistId).subscribe({
      next: () => {
        this.navigateToService.navigateToPlaylists();
      },
      error: (err: any) => {
        alert('Ошибка при удалении плейлиста');
      }
    });
  }

  manageAccess() {
    this.showAccessDialog = true;
  }

  trackByFilmId(index: number, film: PlaylistContentItem): string {
    return film.item.filmid;
  }

  navigateToFilm(filmid: string) {
    this.navigateToService.navigateToFilm(filmid);
  }

  onPlaylistNameChange(newName: string) {
    this.playlistName = newName;
  }

  onPlaylistDescriptionChange(newDescription: string) {
    this.playlistDescription = newDescription;
  }
}
