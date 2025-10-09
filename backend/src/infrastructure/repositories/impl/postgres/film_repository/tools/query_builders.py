from datetime import datetime
from typing import List, Optional

from src.domain.entities.film import FilmPreview
from src.infrastructure.repositories.impl.postgres.film_repository.orm import Film, UserFilm
from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale
from src.web.models.search_filters import BaseBounds, BaseSearchingFilters
from sqlalchemy import and_, func, cast, Float, or_, Integer
from sqlalchemy.dialects.postgresql import array
from urllib.parse import quote


class LocalFilmSearchQueryBuilder:
    def __init__(self, base_query):
        self.query = base_query

    def apply_all(self, filters: BaseSearchingFilters):
        for field, value in filters.get_non_null_fields().items():
            self.apply_filter(field, value)
        return self

    def apply_filter(self, field: str, value: any):
        method_name = f"filter_by_{field}"
        method = getattr(self, method_name, None)
        if method:
            self.query = method(value)

    def filter_by_filmid(self, value: str):
        return self.query.where(Film.filmid == value)

    def filter_by_filmids(self, value: List[str]):
        conditions = []
        for filmid in value:
            conditions.append(Film.filmid == filmid)
            conditions.append(Film.filmid.ilike(f"{filmid}-%"))
        return self.query.where(or_(*conditions))

    def filter_by_name(self, value: str):
        words = value.strip().lower().split()
        conditions = [
            or_(
                func.lower(Film.name).ilike(f"%{word}%"),
                func.lower(Film.alternative_name).ilike(f"%{word}%")
            )
            for word in words
        ]
        conditions.append(Film.name.is_not(None))
        return self.query.where(and_(*conditions))

    def filter_by_person(self, value: str):
        words = value.strip().lower().split()
        if not words:
            return self.query.filter(False)

        json_path_conditions = [
            f'@.name like_regex ".*{word}.*" flag "i"' for word in words
        ]
        full_condition = " && ".join(json_path_conditions)
        json_path = f'$[*]?({full_condition})'
        print(f"Generated JSONPath: {json_path}")  # Для отладки
        return self.query.where(
            func.jsonb_path_exists(Film.persons, json_path)
        )

    def filter_by_is_series(self, value: bool):
        if value:
            return self.query.where(Film.season.is_not(None))

        return self.query.where(Film.season.is_(None))

    def filter_by_kp_rating(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        kp_exists = Film.ratings.has_key('kp')
        kp_rating = cast(Film.ratings['kp'], Float)

        conditions = []

        if value.lower is not None and value.upper is not None:
            if value.lower == value.upper:
                conditions.append(kp_rating == value.lower)
            else:
                conditions.append(kp_rating > value.lower)
                conditions.append(kp_rating <= value.upper)
        elif value.lower is not None:
            conditions.append(kp_rating > value.lower)
        elif value.upper is not None:
            conditions.append(kp_rating < value.upper)

        return self.query.where(and_(kp_exists, *conditions))

    def filter_by_year(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        conditions = [Film.release_year.is_not(None)]

        if value.lower is not None and value.upper is not None:
            if value.lower == value.upper:
                conditions.append(Film.release_year == value.lower)
            else:
                conditions.append(Film.release_year > value.lower)
                conditions.append(Film.release_year <= value.upper)
        elif value.lower is not None:
            conditions.append(Film.release_year > value.lower)
        elif value.upper is not None:
            conditions.append(Film.release_year <= value.upper)

        return self.query.where(and_(*conditions))

    def filter_by_length(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        conditions = [Film.time_minutes.is_not(None)]

        if value.lower is not None and value.upper is not None:
            if value.lower == value.upper:
                conditions.append(Film.time_minutes == value.lower)
            else:
                conditions.append(Film.time_minutes > value.lower)
                conditions.append(Film.time_minutes <= value.upper)
        elif value.lower is not None:
            conditions.append(Film.time_minutes > value.lower)
        elif value.upper is not None:
            conditions.append(Film.time_minutes <= value.upper)

        return self.query.where(and_(*conditions))

    def filter_by_age_rating(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        condition = [Film.age_rating.is_not(None)]

        if value.lower is not None and value.upper is not None:
            if value.lower == value.upper:
                condition.append(Film.age_rating == value.lower)
            else:
                condition.append(Film.age_rating > value.lower)
                condition.append(Film.age_rating <= value.upper)
        elif value.lower is not None:
            condition.append(Film.age_rating > value.lower)
        elif value.upper is not None:
            condition.append(Film.age_rating <= value.upper)

        return self.query.where(and_(*condition))

    def filter_by_genres(self, value: List[str]):
        lowered = [v.lower() for v in value]

        return self.query.where(
            Film.genres.op("?&")(array(lowered))
        )

    def filter_by_countries(self, value: List[str]):
        # lowered = [v.lower() for v in value]

        return self.query.where(
            Film.countries.op("?&")(array(value))
        )

    def filter_by_user_rating(self, value: BaseFilmComplexRating[BaseRatingScale]):
        value = BaseFilmComplexRating[BaseRatingScale].model_validate(value)
        conditions = [UserFilm.user_rating.is_not(None)]
        for field, rating in value:
            if rating is not None:
                conditions.append(
                    UserFilm.user_rating[field].astext.cast(Integer) == rating.value
                )
        if conditions:
            return self.query.where(and_(*conditions))

    def build(self):
        return self.query


class APIFilmSearchQueryBuilder:
    def __init__(self, base_query: str):
        self.query = base_query

    def apply_all(self, filters: BaseSearchingFilters):
        for field, value in filters.get_non_null_fields().items():
            self.apply_filter(field, value)
        return self

    def apply_filter(self, field: str, value: any):
        method_name = f"filter_by_{field}"
        method = getattr(self, method_name, None)
        if method:
            self.query = method(value)

    def filter_by_sort_fields(self, value: List[str]):
        local_query = ""
        for _ in value:
            local_query += f"&sortField={_}"
            local_query += f"&sortType=-1"
        return self.query + local_query

    # season search
    def filter_by_filmid(self, value: str):
        return self.query + f"&movieId={value}"

    def filter_by_seasons_range(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        return self.query + f"&number={value.lower}-{value.upper}"

    def filter_by_page(self, value: int):
        return self.query + f"&page={value}"

    def filter_by_limit(self, value: int):
        return self.query + f"&limit={value}"

    # search by filters
    def filter_by_name(self, value: str):
        query = quote(value) if value else ""
        return self.query + f"&query={query}"

    def filter_by_is_series(self, value: bool):
        return self.query + f"&isSeries={str(value).lower()}"

    def filter_by_year(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        if value.lower is not None and value.upper is not None:
            return self.query + f"&year={value.lower}-{value.upper}"
        if value.lower:
            return self.query + f"&year={value.lower}-2050"
        if value.upper:
            return self.query + f"&year=1900-{value.upper}"

    def filter_by_kp_rating(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        current_year = datetime.now().year
        if value.lower is not None and value.upper is not None:
            return self.query + f"&rating.kp={value.lower}-{value.upper}"
        if value.lower:
            return self.query + f"&rating.kp={value.lower}-{current_year + 1}"
        if value.upper:
            return self.query + f"&rating.kp=0-{value.upper}"

    def filter_by_length(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        if value.lower is not None and value.upper is not None:
            return self.query + f"&movieLength={value.lower}-{value.upper}"
        if value.lower:
            return self.query + f"&movieLength={value.lower}-300"
        if value.upper:
            return self.query + f"&movieLength=0-{value.upper}"

    def filter_by_genres(self, value: List[str]):
        local_query = ""
        for _ in value:
            query = quote(_) if value else ""
            local_query += f"&genres.name={query}"
        return self.query + local_query

    def filter_by_countries(self, value: List[str]):
        local_query = ""
        for _ in value:
            query = quote(_) if value else ""
            local_query += f"&countries.name={query}"
        return self.query + local_query

    def filter_by_age_rating(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        if value.lower is not None and value.upper is not None:
            return self.query + f"&ageRating={value.lower}-{value.upper}"
        if value.lower:
            return self.query + f"&ageRating={value.lower}-18"
        if value.upper:
            return self.query + f"&ageRating=0-{value.upper}"

    def build(self):
        print(f'ОКОНЧАТЕЛЬНЫЙ ЗАПРОС: {self.query}')
        return self.query


class LocalFilmListFilter:
    def __init__(self, films: List[FilmPreview]):
        self.films = films

    def apply_all(self, filters: BaseSearchingFilters) -> Optional[List[FilmPreview]]:
        if not self.films:
            return None

        for field, value in filters.get_non_null_fields().items():
            method = getattr(self, f"filter_by_{field}", None)
            if method:
                self.films = method(value)
        return self.films

    def filter_by_filmid(self, value: str):
        return [film for film in self.films if film.filmid == value]

    def filter_by_name(self, value: str):
        words = value.strip().lower().split()
        return [
            film for film in self.films
            if all(
                word in (film.name or "").lower() or word in (film.alternative_name or "").lower()
                for word in words
            )
        ]

    def filter_by_is_series(self, value: bool):
        return [
            film for film in self.films
            if film.is_series == value
        ]

    def _strict_bounds_check(self, actual_value: Optional[float], bounds: BaseBounds) -> bool:
        if actual_value is None:
            return False

        if bounds.lower is not None and bounds.upper is not None:
            if bounds.lower == bounds.upper:
                return actual_value == bounds.lower
            return actual_value > bounds.lower and actual_value < bounds.upper
        elif bounds.lower is not None:
            return actual_value > bounds.lower
        elif bounds.upper is not None:
            return actual_value < bounds.upper
        return True

    def filter_by_year(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        return [
            film for film in self.films
            if film.release_year is not None and
               self._strict_bounds_check(film.release_year, value)
        ]

    def filter_by_length(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        return [
            film for film in self.films
            if film.time_minutes is not None and
               self._strict_bounds_check(film.time_minutes, value)
        ]

    def filter_by_age_rating(self, value: BaseBounds):
        value = BaseBounds.model_validate(value)
        return [
            film for film in self.films
            if film.age_rating is not None and
               self._strict_bounds_check(film.age_rating, value)
        ]

    def filter_by_genres(self, value: List[str]):
        lowered = set(v.lower() for v in value)
        return [
            film for film in self.films
            if set(g.lower() for g in film.genres).intersection(lowered)
        ]

    def filter_by_countries(self, value: List[str]):
        lowered = set(v.lower() for v in value)
        return [
            film for film in self.films
            if set(c.lower() for c in film.countries).intersection(lowered)
        ]
