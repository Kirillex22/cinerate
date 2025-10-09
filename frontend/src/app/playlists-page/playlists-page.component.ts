import { NgFor } from '@angular/common';
import { NgIf } from '@angular/common';
import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Playlist } from '../models/playlists.interface';
import { Router } from '@angular/router';
import { PlaylistService } from '../services/playlist.service';
import { GradientService } from '../services/gradient.service';
import { MatDialog } from '@angular/material/dialog';
import { CreateSimplePlaylistDialogComponent } from '../playlist-simple-create-dialog/playlist-simple-create-dialog.component';
import { PlaylistGenerateDialogComponent } from '../playlist-generate-dialog/playlist-generate-dialog.component';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-playlists-page',
  standalone: true,
  imports: [CommonModule, NgFor],
  templateUrl: './playlists-page.component.html',
  styleUrl: './playlists-page.component.css'
})
export class PlaylistsPageComponent  implements OnInit {
  playlists: Playlist[] = [];
  playlistGradients: string[] = [];
  isError: boolean = false;

  constructor(
    private playlistService: PlaylistService, 
    private gradientService: GradientService, 
    private router: Router,
    private navigateToService: NavigateService, 
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.playlistService.getPlaylists().subscribe({
      next: playlists => {
      this.playlists = playlists;
      this.playlistGradients = this.playlists.map(() => this.gradientService.getRandomGradient());
      },
      error : () => {
        this.isError = true;
      }
    });
  }

  trackByPlaylistId(index: number, playlist: Playlist): string {
    return playlist.playlistid;
  }

  openCreateDialog() {
    const dialogRef = this.dialog.open(CreateSimplePlaylistDialogComponent, {
      width: '440px',
      disableClose: true
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result && result.created) {
        this.refreshPlaylists();
        this.isError = false
      }
    });
  }

  openGenerateDialog() {
    const dialogRef = this.dialog.open(PlaylistGenerateDialogComponent, {
      width: '540px',
      disableClose: true
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result && result.created) {
        this.refreshPlaylists();
        this.isError = false
      }
    });
  }

  refreshPlaylists() {
    this.playlistService.getPlaylists().subscribe(playlists => {
      this.playlists = playlists;
      this.playlistGradients = this.playlists.map(() => this.gradientService.getRandomGradient());
    });
  }

  navigateToPlaylist(playlistId: string) {
    this.navigateToService.navigateToPlaylist(playlistId);
  }

}
