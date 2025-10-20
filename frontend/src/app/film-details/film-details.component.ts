import { Component, inject, ElementRef, ViewChildren, AfterViewInit, QueryList } from '@angular/core';
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

export class FilmDetailsComponent implements AfterViewInit {
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
          width: '900px',
          maxWidth: '90vw',
          data: { film, ratings: film.user_rating }
        });

        dialogRef.afterClosed().subscribe((result) => {
          if (result) {
            console.log(result)
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
      width: '900px',
      maxWidth: '900vw',
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
    return value ? this.ratingWords[value - 1] : '—';
  }

  @ViewChildren('scrollContainer') scrollContainers!: QueryList<ElementRef<HTMLDivElement>>;

  arrowVisibility: Record<string, boolean> = {};

  scrollListIds = ['director', 'actor', 'episode'];

  ngAfterViewInit() {
    setTimeout(() => {
      this.scrollListIds.forEach(id => {
        this.updateArrows(id);
      });
    }, 300);
  }

  // Элемент прокрутки по id
  private getScrollElement(id: string): HTMLDivElement | undefined {
    // Каждому контейнеру прокрутки назначен #scrollContainer и data-id
    const containerRef = this.scrollContainers.toArray()
      .find(c => c.nativeElement.getAttribute('data-id') === id);
    return containerRef?.nativeElement;
  }

  private getCardWidth(id: string): number {
    const el = this.getScrollElement(id);
    if (!el) return 0;

    let cardSelector = id == 'episode' ? '.episode-card' : '.person-card';
    const card = el.querySelector(cardSelector);
    if (!card) return 0;

    const cardWidth = (card as HTMLElement).offsetWidth;
    const style = getComputedStyle(el);
    const gap = parseInt(style.gap || '0', 10);

    return cardWidth + gap;
  }

  // Видимость стрелок для конкретного списка
  updateArrows(id: string) {
    const el = this.getScrollElement(id);
    if (!el) return;

    let cardSelector = id == 'episode' ? '.episode-card' : '.person-card';
    const cardsCount = el.querySelectorAll(cardSelector).length;

    const needScroll  = id == 'episode' ? 3 : 8;

    // Если карточек мало — стрелки скрываем, иначе — стрелки всегда видны
    this.arrowVisibility[id] = cardsCount > needScroll;
  }

  // Обработчик прокрутки
  onScroll(id: string) {
    this.updateArrows(id);
  }

  // Прокрутка влево
  scrollLeft(id: string) {
    const el = this.getScrollElement(id);
    if (!el) return;

    const scrollCount = id == 'episode' ? 3 : 7;

    const scrollAmount = this.getCardWidth(id) * scrollCount;
    el.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  }

  // Прокрутка вправо
  scrollRight(id: string) {
    const el = this.getScrollElement(id);
    if (!el) return;

    const scrollCount = id == 'episode' ? 3 : 7;

    const scrollAmount = this.getCardWidth(id) * scrollCount;
    el.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  }

  canScrollLeft(id: string): boolean {
    const el = this.getScrollElement(id);
    return el ? el.scrollLeft > 0 : false;
  }

  canScrollRight(id: string): boolean {
    const el = this.getScrollElement(id);
    if (!el) return false;
    return el.scrollLeft + el.clientWidth < el.scrollWidth;
  }
  
}