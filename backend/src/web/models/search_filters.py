from typing import Optional, List, Union
from pydantic import BaseModel, Field

from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale


class BaseBounds(BaseModel):
    lower: Optional[Union[float, int]] = Field(None, description="Нижняя граница")
    upper: Optional[Union[float, int]] = Field(None, description="Верхняя граница")

    def describe(self, label: str = "") -> str:
        if self.lower is not None and self.upper is not None:
            return f"от {self.lower} до {self.upper} {label}".strip()
        elif self.lower is not None:
            return f"от {self.lower} {label}".strip()
        elif self.upper is not None:
            return f"до {self.upper} {label}".strip()
        elif self.upper == self.lower:
            return f"равный {self.upper} {label}".strip()
        return ""


class BaseSearchingFilters(BaseModel):
    filmid: Optional[str] = Field(None, description="Идентификатор фильма")
    filmids: Optional[List[str]] = Field(None, description='Идентификаторы нужных фильмов (работает только локально)')
    name: Optional[str] = Field(None, description="Название фильма")
    person: Optional[str] = Field(None, description="Персона (режиссер или актер), участвовавшая в создании фильма")
    is_series: Optional[bool] = Field(None, description="Является ли сериалом")
    year: Optional[BaseBounds] = Field(None, description="Год релиза")
    kp_rating: Optional[BaseBounds] = Field(None, description="Границы рейтинга кинопоиска")
    length: Optional[BaseBounds] = Field(None, description="Границы длительности в минутах")
    age_rating: Optional[BaseBounds] = Field(None, description="Возрастной рейтинг")
    genres: Optional[List[str]] = Field(None, description="Жанры фильма")
    countries: Optional[List[str]] = Field(None, description="Страны")

    def get_non_null_fields(self) -> dict:
        return {k: v for k, v in self.dict().items() if v is not None}


class SearchingFiltersWithUserData(BaseSearchingFilters):
    is_watched: Optional[bool] = Field(None, description="Был ли уже просмотрен пользователем")
    user_rating: Optional[BaseFilmComplexRating[BaseRatingScale]] = Field(None, description="Оценка пользователя")

    def generate_description(self) -> str:
        start = "Фильмы и сериалы "
        parts = []

        if self.person:
            parts.append(f"с {self.person}")

        if self.countries:
            countries = ", ".join(self.countries)
            parts.append(f"снятые в {countries}")

        if self.genres:
            genres = ", ".join(self.genres)
            parts.append(f"в жанре {genres}")

        if self.year:
            parts.append(f"выпущенные {self.year.describe('году')}")

        if self.kp_rating:
            parts.append(f"с рейтингом {self.kp_rating.describe('на Кинопоиске')}")

        if self.length:
            parts.append(f"длительностью {self.length.describe('')}")

        if self.age_rating:
            parts.append(f"с возрастным рейтингом {self.age_rating.describe('')}")

        if self.is_series is not None:
            start = "Cериалы " if self.is_series else "Фильмы "

        if self.is_watched is not None:
            parts.append("уже просмотренные" if self.is_watched else "ещё не просмотренные")

        if self.user_rating:
            rating_parts = []
            for attr, value in self.user_rating:
                if value is not None:
                    if value.name == 'AWESOME':
                        translated_value = 'отлично'
                    elif value.name == 'GOOD':
                        translated_value = 'хорошо'
                    elif value.name == 'NORMAL':
                        translated_value = 'нормально'
                    elif value.name == 'BAD':
                        translated_value = 'плохо'
                    else:
                        translated_value = value.name
                    label = self.user_rating.model_fields[attr].description or attr
                    rating_parts.append(f"{label.lower()} — {translated_value}")
            if rating_parts:
                parts.append("по пользовательским оценкам: " + ", ".join(rating_parts))

        return start + ", ".join(parts)


class ApiExtension(BaseModel):
    page: Optional[int] = Field(default=1, description="Кол-во страниц в ответе от API")
    limit: Optional[int] = Field(default=150, description="Кол-во элементов на странице в ответе от API")
    sort_fields: Optional[List[str]] = Field(["votes.kp", "rating.kp"], description="Поля для сортировки ответа API")
    sort_type: Optional[str] = Field(None, description="Тип сортировки в API")
    seasons_range: Optional[BaseBounds] = Field(None, description="Границы сезонов сериала для получения")

    def get_non_null_fields(self) -> dict:
        return {k: v for k, v in self.dict().items() if v is not None}

    def get_non_null_fileds_exclude_extension(self) -> dict:
        filters = BaseSearchingFilters(**self.model_dump())
        return filters.get_non_null_fields()


class BaseApiSearchingFilters(BaseSearchingFilters, ApiExtension):
    pass
