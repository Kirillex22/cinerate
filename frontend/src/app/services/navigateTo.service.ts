import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})

export class NavigateService {
  constructor(private router: Router) { }

  navigateToFilm(filmId: string) {
    this.router.navigate(['/film', filmId]);
  }

  navigateToPlane() {
    console.log('Выполняется переход на /plane'); // Добавим лог для проверки
    this.router.navigate(['/plane']);
  }

  navigateToPlaylist(playlistId: string) {
    this.router.navigate(['/playlist', playlistId]);
  }

  navigateToPlaylists() {
    this.router.navigate(['/playlists']);
  }

  navigateToProfile(id: string) {
    this.router.navigate(['/profile', id]);
  }

  navigateToProfileInNewWindow(userId: string) {
    if (typeof window !== 'undefined') {
      window.open(`/profile/${userId}`, '_blank');
    }
  }

  navigateToSubscribers(userid: string) {
    this.router.navigate(['/profile', userid, 'subscribers']);
  }

  navigateToSubscriptions(userid: string) {
    this.router.navigate(['/profile', userid, 'subscriptions']);
  }

  navigateToLogin() {
    this.router.navigate(['/login']);
  }

  navigateToRegister() {
    this.router.navigate(['/register']);
  }
}
