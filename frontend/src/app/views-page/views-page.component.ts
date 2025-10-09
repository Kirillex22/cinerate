import { Component, OnInit } from '@angular/core';
import { FilmService } from '../services/film.service';
import { FilmDetails } from '../models/film-details.interface';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { RatingDialogComponent } from '../rating-dialog/rating-dialog.component';
import { CommonModule } from '@angular/common';
import { NavigateService } from '../services/navigateTo.service';

@Component({
  selector: 'app-views-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './views-page.component.html',
  styleUrl: './views-page.component.css'
})
export class ViewsPageComponent implements OnInit {
  watchedFilms: FilmDetails[] = [];
  isError: boolean = false;
  ratingWords = ['Плохо', 'Нормально', 'Хорошо', 'Отлично'];
  characteristics = [
    { key: 'acting_game', label: 'Актёрская игра' },
    { key: 'atmosphere', label: 'Атмосфера' },
    { key: 'montage', label: 'Монтаж' },
    { key: 'music', label: 'Музыка' },
    { key: 'originality', label: 'Оригинальность' },
    { key: 'storyline', label: 'Сюжет' },
  ];

  constructor(
    private filmService: FilmService, 
    private navigateToService: NavigateService,
    private router: Router, 
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.filmService.getWatchedFilms().subscribe({
      next: films => {
        this.watchedFilms = films;
      },
      error: () => {
        this.isError = true;
      }
    });
  }

  openRatingDialog(film: FilmDetails) {
    const dialogRef = this.dialog.open(RatingDialogComponent, {
      data: { film, ratings: film.user_rating }
    });
    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.filmService.rateFilm(film.filmid, result).subscribe(() => {
          film.user_rating = result;
        });
      }
    });
  }

  getUserRatingWord(film: FilmDetails, key: string): string {
    if (!film.user_rating) return '-';
    const value = film.user_rating[key as keyof typeof film.user_rating];
    if (!value) return '-';
    return this.ratingWords[value - 1] || '-';
  }

  getRatingClass(film: FilmDetails, key: string): string {
    if (!film.user_rating) return '';
    const value = film.user_rating[key as keyof typeof film.user_rating];
    switch (value) {
      case 1: return 'bad';
      case 2: return 'normal';
      case 3: return 'good';
      case 4: return 'excellent';
      default: return '';
    }
  }

  navigateToFilm(filmId: string) {
    this.navigateToService.navigateToFilm(filmId);
  }
}
