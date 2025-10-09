from src.domain.entities.film import FilmPreview, FilmExtended
from src.shared.tools.api_clients.core.base_external_api_client import BaseExternalAPIClient
from src.infrastructure.repositories.core.base_film_repositories import BaseExternalSearchFilmRepository
from typing import List, Optional

from src.infrastructure.repositories.impl.postgres.film_repository.tools.query_builders import LocalFilmListFilter
from src.services.film.exceptions import MissingSearchFilterException, MissingGetFilterException, \
    MissingSeasonsFilterException, NotFoundExternalException
from src.web.models.search_filters import BaseApiSearchingFilters


class KpApiSearchFilmRepository(BaseExternalSearchFilmRepository):
    def __init__(self, api_client: BaseExternalAPIClient):
        self._api_client = api_client

    def search_by_name(self, filters: BaseApiSearchingFilters) -> Optional[List[FilmPreview]]:
        if filters.name:
            api_result = self._api_client.search_by_name(filters)

            co_filter = LocalFilmListFilter(api_result)
            final_result = co_filter.apply_all(filters)

            return final_result

        raise MissingSearchFilterException(filters)

    def search_by_filters(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        api_result = self._api_client.search_by_filters(filters)

        if api_result is None:
            raise NotFoundExternalException(filters)

        return api_result

    def get(self, filters: BaseApiSearchingFilters) -> Optional[FilmExtended]:
        if filters.filmid:
            return self._api_client.get(filters)

        raise MissingGetFilterException(filters)

    def get_seasons(self, filters: BaseApiSearchingFilters) -> List[FilmExtended]:
        if filters.filmid and filters.is_series is True:
            return self._api_client.get_all_seasons(filters)

        raise MissingSeasonsFilterException(filters)
