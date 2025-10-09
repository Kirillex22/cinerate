import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FilmService } from '../services/film.service';
import { Film } from '../models/film.interface';
import { NgFor, NgIf } from '@angular/common';
import { Router } from '@angular/router';
import { NavigateService } from '../services/navigateTo.service';


@Component({
  selector: 'app-plane-page',
  standalone: true,
  imports: [CommonModule, NgFor, NgIf],
  templateUrl: './plane-page.component.html',
  styleUrls: ['./plane-page.component.css']
})

export class PlanePageComponent implements OnInit {
  films: Film[] = [];
  hoveredFilm: Film | null = null;
  isError: boolean = false;

  constructor(
    private filmService: FilmService,
    private navigateToService: NavigateService,  
    private router: Router
  ) {}

  ngOnInit() {
    this.filmService.getUnwatchedFilms().subscribe({
    next: films => {
      this.films = films;
    },
    error: () => {
      this.isError = true;
    }
  });
  }

  showFilmInfo(film: Film) {
    this.hoveredFilm = film;
  }

  hideFilmInfo() {
    this.hoveredFilm = null;
  }

  trackByFilmId(index: number, film: Film): string {
    return film.filmid;
  }

  navigateToFilm(filmId: string) {
    this.navigateToService.navigateToFilm(filmId);
  }
}