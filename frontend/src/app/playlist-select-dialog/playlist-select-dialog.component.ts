import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog, MatDialogModule } from '@angular/material/dialog';
import { PlaylistService } from '../services/playlist.service';
import { Playlist } from '../models/playlists.interface';
import { FilmDetails } from '../models/film-details.interface';
import { CreateSimplePlaylistDialogComponent } from '../playlist-simple-create-dialog/playlist-simple-create-dialog.component';
import { CommonModule } from '@angular/common';
import { GradientService } from '../services/gradient.service';

@Component({
  selector: 'app-playlist-select-dialog',
  imports: [CommonModule, MatDialogModule],
  templateUrl: './playlist-select-dialog.component.html',
  styleUrls: ['./playlist-select-dialog.component.css']
})
export class PlaylistSelectDialogComponent {
  playlists: Playlist[] = [];
  playlistGradients: string[] = [];
  loading = true;
  errorMsg: string | null = null;

  constructor(
    private playlistService: PlaylistService,
    private dialogRef: MatDialogRef<PlaylistSelectDialogComponent>,
    private dialog: MatDialog,
    private gradientService: GradientService,
    @Inject(MAT_DIALOG_DATA) public data: { film: FilmDetails }
  ) {}

  ngOnInit() {
    this.loadPlaylists();
  }

  loadPlaylists() {
    this.loading = true;
    this.playlistService.getPlaylists().subscribe(playlists => {
      this.playlists = playlists;
      this.playlistGradients = this.playlists.map(() => this.gradientService.getRandomGradient());
      this.loading = false;
    });
  }

  addToPlaylist(playlist: Playlist) {
    this.errorMsg = null;
    this.playlistService.addFilmToPlaylist(playlist.playlistid, this.data.film.filmid)
      .subscribe({
        next: () => this.dialogRef.close({ added: true }),
        error: (err) => {
          if (err.error && err.error.detail && err.error.detail.includes('already')) {
            this.errorMsg = 'Фильм уже есть в этом плейлисте';
          } else {
            this.errorMsg = 'Ошибка при добавлении фильма';
          }
        }
      });
  }

  openCreateDialog() {
    const dialogRef = this.dialog.open(CreateSimplePlaylistDialogComponent, {
      width: '400px'
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result && result.created) {
        this.loadPlaylists();
      }
    });
  }

  onSave() {
    this.dialogRef.close(this.playlists);
  }

  onCancel() {
    this.dialogRef.close();
  }
}