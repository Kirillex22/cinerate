from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List
from datetime import datetime
from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale
from enum import Enum


class Person(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    photo: Optional[str] = None
    en_profession: Optional[str] = None


class Episode(BaseModel):
    number: int
    name: Optional[str]
    en_name: Optional[str] = None
    air_date: Optional[datetime] = None
    description: Optional[str] = None
    preview_link: Optional[HttpUrl] = None


class SeasonInfo(BaseModel):
    number: int
    episodes_count: Optional[int]


class FilmBase(BaseModel):
    filmid: str = Field(..., description="Идентификатор фильма во внешнем API")


class FilmPersonal(FilmBase):
    season: Optional[int] = Field(None, description="Номер сезона")
    is_series: Optional[bool] = Field(None, description="Является ли сериалом")
    seasons_info: Optional[List[SeasonInfo]] = Field(None, description="Общая информация о сезонах сериала")
    already_added: Optional[bool] = Field(None, description="Был ли уже добавлен пользователем")
    is_watched: Optional[bool] = Field(None, description="Был ли уже просмотрен пользователем")
    user_rating: Optional[BaseFilmComplexRating[BaseRatingScale]] = Field(None, description="Оценка пользователя")
    last_updated: Optional[datetime] = Field(None, description="Дата последнего обновления информации")
    added_at: Optional[datetime] = Field(None, description="Дата добавления фильма пользователем")
    playlists: Optional[List[str]] = Field(None, description="Названия плейлистов, в которые входит.")


class FilmPreview(FilmPersonal):
    name: str = Field(..., description="Название фильма")
    poster_link: Optional[HttpUrl] = Field(None, description="Ссылка на постер")
    release_year: Optional[int] = Field(None, description="Год релиза")
    alternative_name: Optional[str] = Field(None, description="Исходное название фильма")
    genres: List[str] = Field(..., description="Список жанров")
    countries: List[str] = Field(..., description="Список стран")
    director: Optional[str] = Field(None, description="Режиссер")
    time_minutes: Optional[int] = Field(None, description="Длительность в минутах")
    age_rating: Optional[int] = Field(None, description="Возрастной рейтинг")


class FilmExtended(FilmPersonal):
    name: str = Field(..., description="Название фильма")
    poster_link: Optional[HttpUrl] = Field(None, description="Ссылка на постер")
    alternative_name: Optional[str] = Field(None, description="Исходное название фильма")
    release_year: Optional[int] = Field(None, description="Год релиза")
    genres: List[str] = Field(..., description="Список жанров")
    slogan: Optional[str] = Field(None, description="Слоган фильма")
    countries: List[str] = Field(..., description="Список стран")
    director: Optional[str] = Field(None, description="Режиссер")
    description: Optional[str] = Field(None, description="Описание фильма")
    age_rating: Optional[int] = Field(None, description="Возрастной рейтинг")
    persons: Optional[List[Person]] = Field(None, description="Каст фильма + режиссеры")
    time_minutes: Optional[int] = Field(None, description="Длительность в минутах")
    ratings: Optional[dict[str, Optional[float]]] = Field(None, description="Оценки по разным рейтингам")
    trailers: Optional[List[str]] = Field(None, description="Ссылки на трейлеры")
    end_year: Optional[int] = Field(None, description="Год окончания съемок")
    status: Optional[str] = Field(None, description="Этап производства")
    tops: Optional[List[str]] = Field(None, description="Позиции в топах")
    episodes: Optional[List[Episode]] = Field(None, description="Описание серий")

    @validator('episodes')
    def sort_episodes(cls, v):
        if v:
            return sorted(v, key=lambda ep: ep.number)
        return v


class FilmTypes(Enum):
    FILM_PREVIEW = 'FilmPreview'
    FILM_EXTENDED = 'FilmExtended'
