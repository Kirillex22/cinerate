import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap } from 'rxjs';
import { Film} from '../models/film.interface';
import { FilmDetails } from '../models/film-details.interface';
import { FilmDetailsResponse } from '../models/film-details.interface';
import { BASE_URL } from '../models/config';

@Injectable({
  providedIn: 'root'
})
export class FilmService {
  private baseUrl = BASE_URL;
  constructor(private http: HttpClient) { }

  getUnwatchedFilms(): Observable<Film[]> {
    return this.http.get<Film[]>(`${this.baseUrl}films/list`, {
      params: { watched: 'false' },
      withCredentials: true
    });
  }

  getWatchedFilms(): Observable<FilmDetails[]> {
    return this.http.get<FilmDetails[]>(`${this.baseUrl}films/list`, {
      params: { watched: 'true' },
      withCredentials: true
    });
  }

  getFilmDetails(filmId: string, isSeries: boolean) {
    return this.http.post<FilmDetailsResponse>(`${this.baseUrl}films/local/get`, {
      filmid: filmId,
      is_series: isSeries
    }, {
      withCredentials: true
    });
  }

  deleteFilmFromWatchList(filmId: string) {
    return this.http.delete<any>(`${this.baseUrl}films`, {
      headers: { 'Content-Type': 'application/json' },
      body: { filmid: filmId },
      withCredentials: true
    });
  }

  addFilmToWatchList(filmId: string): Observable<any> {
    return this.getFilmDetails(filmId, false).pipe(
      switchMap(filmData => {
        return this.http.post<any>(`${this.baseUrl}films/unwatched`, filmData, {
          withCredentials: true
        });
      })
    );
  }

  setWatchStatus(filmId: string, stat: boolean) {
    return this.http.post(`${this.baseUrl}films/watch-status`,
      { filmid: filmId },
      {
        params: { status: stat.toString() },
        withCredentials: true
      }
    );
  }

  rateFilm(filmId: string, ratings: any) {
    return this.http.post(`${this.baseUrl}films/rate`, {
      film: { filmid: filmId },
      rating: ratings
    }, {
      withCredentials: true
    });
  }

  searchLocalFilms(params: any): Observable<any[]> {
    return this.http.post<any[]>(`${this.baseUrl}films/search/local`, params, {
      withCredentials: true
    });
  }

  searchExternalFilms(params: any): Observable<any[]> {
    return this.http.post<any[]>(`${this.baseUrl}films/search/external`, params, {
      withCredentials: true
    });
  }

}
