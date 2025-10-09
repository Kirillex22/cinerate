import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { FilmService } from '../services/film.service';
import { FilmDetails, FilmDetailsResponse, UserRating } from '../models/film-details.interface';
import { catchError, distinctUntilChanged, map, shareReplay, switchMap, tap } from 'rxjs/operators';
import { EMPTY, Observable, of } from 'rxjs';
import { CommonModule } from '@angular/common';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { RatingDialogComponent } from '../rating-dialog/rating-dialog.component';
import { PlaylistSelectDialogComponent } from '../playlist-select-dialog/playlist-select-dialog.component';

@Component({
  selector: 'app-film-details',
  standalone: true,
  imports: [CommonModule, MatDialogModule],
  templateUrl: './film-details.component.html',
  styleUrls: ['./film-details.component.css']
})
export class FilmDetailsComponent {
  private route = inject(ActivatedRoute);
  private filmService = inject(FilmService);
  private dialog = inject(MatDialog);
  film$!: Observable<FilmDetails>;
  is_watched = false;
  already_added = false;

  ratingWords = ['Плохо', 'Нормально', 'Хорошо', 'Отлично'];
  characteristics = [
    { key: 'acting_game', label: 'Актёрская игра' },
    { key: 'atmosphere', label: 'Атмосфера' },
    { key: 'montage', label: 'Монтаж' },
    { key: 'music', label: 'Музыка' },
    { key: 'originality', label: 'Оригинальность' },
    { key: 'storyline', label: 'Сюжет' },
  ];

  ngOnInit() {
    this.loadFilm();
  }

  loadFilm() {
    this.film$ = this.route.paramMap.pipe(
      map(paramMap => paramMap.get('id')!),
      distinctUntilChanged(),
      switchMap(id =>
        this.filmService.getFilmDetails(id, false).pipe(
          map((resp: FilmDetailsResponse) => Array.isArray(resp) ? resp[0] : resp),
          tap(film => {
            this.is_watched = film.is_watched;
            this.already_added = film.already_added ?? false;
          })
        )
      ),
    );
  }

  toggleWatched(film: FilmDetails) {
    if (!film) return;

    if (!film.is_watched) {
      this.filmService.setWatchStatus(film.filmid, true).subscribe(() => {
        film.is_watched = true;
        this.is_watched = true;

        const dialogRef = this.dialog.open(RatingDialogComponent, {
          data: { film, ratings: film.user_rating }
        });

        dialogRef.afterClosed().subscribe((result) => {
          if (result) {
            this.filmService.rateFilm(film.filmid, result).subscribe(() => {
              film.user_rating = result;
            });
          }
        });
      });
    } else {
      this.filmService.setWatchStatus(film.filmid, false).subscribe(() => {
        film.is_watched = false;
        film.user_rating = null;
        this.is_watched = false;
      });
    }
  }

  addToWatchList(film: FilmDetails) {
    if (!film) return;
    if (film.is_watched == null) {
      this.filmService.addFilmToWatchList(film.filmid).subscribe(() => {
        this.already_added = true;
        this.loadFilm();
      });
    } else {
      this.filmService.deleteFilmFromWatchList(film.filmid).subscribe(() => {
        this.already_added = false;
        this.loadFilm();
      });
    }
  }

  openPlaylistDialog(film: FilmDetails) {
    this.dialog.open(PlaylistSelectDialogComponent, {
      width: '600px',
      data: { film }
    });
  }

  getPersonsByProfession(film: FilmDetails, profession: string) {
    return film?.persons.filter((p: any) => p.en_profession === profession) || [];
  }

  getEpisodes(film: FilmDetails) {
    return film?.episodes || [];
  }

  getUserRatingWord(film: FilmDetails, key: string): string {
    const k = key as keyof UserRating;
    const value = film?.user_rating?.[k];
    return value ? this.ratingWords[value - 1] : '-';
  }
}