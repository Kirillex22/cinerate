import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FilmService } from '../services/film.service';
import { Router } from '@angular/router';
import { SearchStateService } from '../services/search-state.service';
import { NavigateService } from '../services/navigateTo.service';
import { GENRE_LIST } from '../models/config';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-search-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search-page.component.html',
  styleUrls: ['./search-page.component.css']
})
export class SearchPageComponent {
  searchParams: any = {
    name: '',
    person: '',
    genres: [],
    year: { lower: undefined, upper: undefined },
    kp_rating: { lower: undefined, upper: undefined },
    length: { lower: undefined, upper: undefined },
    age_rating: { lower: undefined, upper: undefined },
    is_series: undefined,
  };
  films: any[] = [];
  isExternal = false;
  isFireShow = false;
  errorMsg = '';

  genreInput = '';
  genresList = GENRE_LIST;

  hoveredFilm: any = null;

  dialogVisible = false;
  dialogSeasons: any[] = [];
  dialogFilm: any = null;

  constructor(
    private filmService: FilmService,
    private router: Router,
    private searchState: SearchStateService,
    private navigateToService: NavigateService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    if (this.searchState.searchParams) {
      this.searchParams = JSON.parse(JSON.stringify(this.searchState.searchParams));
      this.films = this.searchState.films;
      this.isExternal = this.searchState.isExternal;
      this.isFireShow = this.searchState.isFireShow;
    } else {
      this.search();
    }
  }

  search() {
    const params = this.cleanParams(this.searchParams);
    if (this.isExternal){
      this.searchParams.person = '';
      this.searchParams.kp_rating.lower = undefined;
      this.searchParams.kp_rating.upper = undefined;
    }

    const search$ = this.isExternal
      ? this.filmService.searchExternalFilms(params)
      : this.filmService.searchLocalFilms(params);

    search$.subscribe({
      next: films => {
        this.films = films;
        this.errorMsg = '';
        this.searchState.searchParams = JSON.parse(JSON.stringify(this.searchParams));
        this.searchState.films = films;
        this.searchState.isExternal = this.isExternal;
        this.searchState.isFireShow = this.isFireShow;
      },
      error: err => {
        this.films = [];
        this.errorMsg = 'Ошибка поиска. Попробуйте изменить фильтры или повторить позже.';
      }
    });
  }

  cleanParams(params: any) {
    const cleaned: any = {};
    for (const key in params) {
      const value = params[key];
      if (Array.isArray(value) && value.length > 0) {
        cleaned[key] = value;
      } else if (typeof value === 'object' && value !== null) {
        const nested = this.cleanParams(value);
        if (Object.keys(nested).length > 0) {
          cleaned[key] = nested;
        }
      } else if (
        value !== undefined &&
        value !== null &&
        value !== ''
      ) {
        cleaned[key] = value;
      }
    }
    return cleaned;
  }

  addGenre() {
    if (this.genreInput && !this.searchParams.genres.includes(this.genreInput)) {
      this.searchParams.genres.push(this.genreInput);
      this.genreInput = '';
    }
  }

  removeGenre(genre: string) {
    this.searchParams.genres = this.searchParams.genres.filter((g: string) => g !== genre);
  }

  showFilmInfo(film: any) {
    this.hoveredFilm = film;
  }

  hideFilmInfo() {
    this.hoveredFilm = null;
  }

  trackByFilmId(index: number, film: any): string {
    return film.filmid;
  }

  onFilmPosterClick(film: any) {
    this.filmService.getFilmDetails(film.filmid, film.is_series).subscribe((details: any) => {
      if (Array.isArray(details)) {
        // сериал, показываем диалог
        this.dialogVisible = true;
        this.dialogSeasons = details.map((d: any) => d.season);
        this.dialogSeasons.sort((a, b) => a - b);
        this.dialogFilm = { ...film, detailsArray: details };
      } else {
        // фильм, сразу открываем новую вкладку
        window.open(`/film/${film.filmid}`, '_blank');
      }
    });
  }

  onSelectSeason(season: number) {
    if (!this.dialogFilm) return;
    const filmid = this.dialogFilm.detailsArray.find((d: any) => d.season === season)?.filmid || this.dialogFilm.filmid;
    window.open(`/film/${filmid}`, '_blank');
  }

  onDialogClose() {
    this.dialogVisible = false;
    this.dialogSeasons = [];
    this.dialogFilm = null;
  }

  onAddAllSeasons() {
    if (!this.dialogFilm || !this.dialogFilm.detailsArray) return;
    const filmids = this.dialogFilm.detailsArray.map((d: any) => d.filmid);
    Promise.all(
      filmids.map((id: string) => this.filmService.addFilmToWatchList(id).toPromise())
    ).then(() => {
      this.snackBar.open('Все сезоны добавлены в запланированно.', 'Закрыть', {
        duration: 5000,
        verticalPosition: 'bottom',
        panelClass: ['green-snackbar']
      });
      this.onDialogClose();
    }).catch(() => {
      this.snackBar.open('Ошибка при добавлении.', 'Закрыть', {
        duration: 5000,
        verticalPosition: 'bottom',
        panelClass: ['red-snackbar']
      });
    });
  }

  navigateToFilm(filmId: string) {
    this.navigateToService.navigateToFilm(filmId);
  }

}
