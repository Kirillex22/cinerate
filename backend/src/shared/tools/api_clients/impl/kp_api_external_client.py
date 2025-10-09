from datetime import datetime
from typing import List, Optional
import httpx
from urllib.parse import quote

from src.shared.tools.api_clients.core.base_external_api_client import BaseExternalAPIClient
from src.domain.entities.film import FilmExtended, FilmPreview
from src.infrastructure.repositories.impl.postgres.film_repository.tools.query_builders import APIFilmSearchQueryBuilder
from src.web.models.search_filters import BaseApiSearchingFilters, BaseBounds
from src.shared.mappers.api_responses_to_models import parse_film_extended, parse_film_preview, parse_episode


def from_iso_to_year(date: str) -> int:
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").year


def drop_invalid_seasons_nums(seasons_nums: list) -> list:
    new_seasons_nums = []
    for season in seasons_nums:
        if season > 0:
            new_seasons_nums.append(season)

    return new_seasons_nums


def disable_search_improves(filters: BaseApiSearchingFilters) -> BaseApiSearchingFilters:
    filters.sort_fields = None
    filters.sort_type = None
    return filters


class KpExternalAPIClient(BaseExternalAPIClient):
    def __init__(
            self,
            kp_url: str,
            api_key: str
    ) -> None:

        self.kp_url = kp_url
        self.api_key = api_key
        self.timeout = 10
        self.headers = {
            f'X-API-KEY': self.api_key,
            'accept': 'application/json',
        }

    def get_response(self, url):
        try:
            response = httpx.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            return None
        except ValueError as e:
            print(f"JSON decode error: {e}")
            return None

    def get(self, filters: BaseApiSearchingFilters) -> Optional[FilmExtended]:
        query = self.kp_url + f"/movie/{filters.filmid}"
        response = self.get_response(query)

        if not response:
            return None

        return parse_film_extended(response)

    def search_by_filters(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        query_bld = APIFilmSearchQueryBuilder(self.kp_url + "/movie?")
        query = query_bld.apply_all(filters).build()
        response = self.get_response(query)

        if not response:
            return []

        data = response.get('docs', [])

        preview_films = []

        for elem in data:
            film_preview = parse_film_preview(elem)
            preview_films.append(film_preview)

        return preview_films

    def search_by_name(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        name = filters.name
        page = filters.page
        limit = filters.limit

        query = quote(name) if name else ""
        param = f"/movie/search?page={page}&limit={limit}&query={query}"
        url = self.kp_url + param
        response = self.get_response(url)

        films_data = response.get('docs', []) if response else {}

        if len(films_data) == 0:
            return []

        return [parse_film_preview(film) for film in films_data]

    def search_seasons(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        filters = disable_search_improves(
            filters)  # убираем параметры, делающие поиск релевантным, так как апи в данном методе их не поддерживает
        query_bld = APIFilmSearchQueryBuilder(self.kp_url + "/season?")
        query = query_bld.apply_all(filters).query
        response = self.get_response(query)

        if not response:
            return []

        data = response.get('docs', [])

        film_extended = self.get(BaseApiSearchingFilters(filmid=filters.filmid))
        if not film_extended:
            return []

        preview_films = []

        for curr_film in data:
            air_date = curr_film.get("airDate")
            film_preview = FilmPreview(
                **film_extended.model_dump()
            )
            film_preview.season = curr_film.get('number')
            film_preview.release_year = from_iso_to_year(air_date) if air_date else None
            preview_films.append(film_preview)

        return preview_films

    def get_all_seasons(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        filters = disable_search_improves(
            filters)
        film_extended = self.get(BaseApiSearchingFilters(filmid=filters.filmid))
        nums_of_seasons = drop_invalid_seasons_nums([si.number for si in film_extended.seasons_info])
        filters.seasons_range = BaseBounds(lower=min(nums_of_seasons), upper=max(nums_of_seasons))

        query_bld = APIFilmSearchQueryBuilder(self.kp_url + "/season?")
        query = query_bld.apply_all(filters).build()

        response = self.get_response(query)

        if not response:
            return []

        data = response.get('docs', [])

        if not film_extended:
            return []

        extended_films = []

        for curr_film in data:
            air_date = curr_film.get("airDate", None)
            film_extended = FilmExtended(
                **film_extended.model_dump()
            )
            film_extended.season = curr_film.get('number', None)
            film_extended.release_year = from_iso_to_year(air_date) if air_date else None
            film_extended.episodes = [parse_episode(episode) for episode in
                                      curr_film.get('episodes', None)] if curr_film.get('episodes', None) else None
            extended_films.append(film_extended)

        return extended_films
