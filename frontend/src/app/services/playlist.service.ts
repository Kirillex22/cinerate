import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Playlist } from '../models/playlists.interface';
import { PlaylistContentResponse } from '../models/playlist-details.interface';
import { BASE_URL } from '../models/config';

@Injectable({
  providedIn: 'root'
})

export class PlaylistService {
  private baseUrl = BASE_URL;
  constructor(private http: HttpClient) { }

  getPlaylists(): Observable<Playlist[]> {
    return this.http.post<Playlist[]>(`${this.baseUrl}playlists/get`, {}, {
      withCredentials: true
    });
  }

  getPlaylistsForTargetUser(userId: string): Observable<Playlist[]> {
    return this.http.post<Playlist[]>(`${this.baseUrl}playlists/get`, {
      target_user: { userid: userId }
    }, {
      withCredentials: true
    });
  }

  getPlaylistContent(playlistid: string): Observable<PlaylistContentResponse> {
    return this.http.post<PlaylistContentResponse>(`${this.baseUrl}playlists/content`, { playlistid }, {
      withCredentials: true
    });
  }

  addFilmToPlaylist(playlistid: string, filmid: string) {
    return this.http.post(`${this.baseUrl}playlists/add`, {
      filters: { playlistid },
      target_film: { filmid }
    }, {
      withCredentials: true
    });
  }

  removeFilmFromPlaylist(playlistid: string, filmid: string) {
    return this.http.post<null>(`${this.baseUrl}playlists/remove-film`, {
      filters: { playlistid },
      target_film: { filmid }
    }, {
      withCredentials: true
    });
  }

  createSimplePlaylist(name: string, description: string, is_public: boolean) {
    return this.http.post<string>(`${this.baseUrl}playlists/create`, {
      name,
      description,
      is_public,
      gen_attrs: null
    }, {
      withCredentials: true
    });
  }

  removePlaylist(playlistId: string) {
    return this.http.delete<string>(`${this.baseUrl}playlists/remove`, {
      headers: { 'Content-Type': 'application/json' },
      body: { playlistid: playlistId },
      withCredentials: true
    });
  }

  generatePlaylist(name: string, description: string, is_public: boolean, gen_attrs: any) {
    return this.http.post<string>(`${this.baseUrl}playlists/create`, {
      name,
      description,
      is_public,
      gen_attrs
    }, {
      withCredentials: true
    });
  }

  getPlaylistDetails(playlistid: string) {
    return this.http.post<any>(`${this.baseUrl}playlists/get`, { playlistid }, {
      withCredentials: true
    });
  }

  setPlaylistPublicity(playlistid: string, publicity: boolean) {
    return this.http.post<any>(`${this.baseUrl}playlists/set-publicity?publicity=${publicity}`, { playlistid }, {
      withCredentials: true
    });
  }

  setPlaylistName(playlistid: string, name: string) {
    return this.http.post<any>(`${this.baseUrl}playlists/set-name?name=${name}`, { playlistid }, {
      withCredentials: true
    });
  }

  setPlaylistDescription(playlistid: string, description: string) {
    return this.http.post<any>(`${this.baseUrl}playlists/set-description?description=${description}`, { playlistid }, {
      withCredentials: true
    });
  }

  addCollaborator(playlistid: string, userid: string) {
    return this.http.post<any>(`${this.baseUrl}playlists/add-collaborator`, {
      filters: { playlistid },
      collaborator: { userid }
    }, {
      withCredentials: true
    });
  }

  removeCollaborator(playlistid: string, userid: string) {
    return this.http.post<any>(`${this.baseUrl}playlists/remove-collaborator`, {
      filters: { playlistid },
      collaborator: { userid }
    }, {
      withCredentials: true
    });
  }

}
