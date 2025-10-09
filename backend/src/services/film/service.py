import asyncio
import re
from typing import List, Optional, Union
from src.domain.entities.film import FilmPreview, FilmExtended, FilmPersonal, FilmTypes
from src.domain.policies.impl.kp_series_to_film import BaseSeriesToFilmPolicy
from src.infrastructure.repositories.core.base_film_repositories import BaseFilmOperationsRepository, BaseLocalSearchFilmRepository, \
    BaseExternalSearchFilmRepository
from src.services.film.exceptions import *
from src.web.models.film_rating import BaseFilmComplexRating
from src.web.models.search_filters import BaseSearchingFilters, BaseApiSearchingFilters


def list_response_resolver(response: List):
    if len(response) == 0:
        return None
    if len(response) == 1:
        return response[0]
    return response


async def local_search_wrapper(func) -> Union[FilmExtended, List[FilmExtended]]:
    try:
        response = func()
        return list_response_resolver(response)
    except NotFoundLocalException:
        pass


class FilmService:
    def __init__(
            self,
            local_search_repository: BaseLocalSearchFilmRepository,
            external_search_repository: BaseExternalSearchFilmRepository,
            operations_repository: BaseFilmOperationsRepository,
            series_to_film_policy: BaseSeriesToFilmPolicy
    ):
        self.__local_search_repository = local_search_repository
        self.__external_search_repository = external_search_repository
        self.__operations_repository = operations_repository
        self.__series_to_film_policy = series_to_film_policy

    def get_series_to_film_policy(self):
        return self.__series_to_film_policy

    def local_search_by_filters(self, user: Optional[User], filters: BaseSearchingFilters,
                                out_model: FilmTypes = FilmTypes.FILM_PREVIEW) -> Union[List[
        FilmPreview], List[FilmExtended]]:
        previews = self.__local_search_repository.search_by_filters(user, filters, out_model)
        if not previews:
            return []

        return previews

    def __set_already_added_flag_to_search_results(self, user: User, previews: List[FilmPreview]) -> List[
        FilmPreview]:
        filmids = [film.filmid for film in previews]
        mask_filter = BaseSearchingFilters(filmids=filmids)
        found_films = self.__local_search_repository.search_by_filters(user, mask_filter)
        if found_films is not None:
            found_filmids = [re.sub(r'-.*', '', film.filmid) for film in found_films]
            for film in previews:
                if re.sub(r'-.*', '', film.filmid) in found_filmids:
                    film.already_added = True

        return previews

    async def external_search_by_filters(self, filters: BaseApiSearchingFilters, user: Optional[User] = None) -> List[
        FilmPreview]:

        if not filters.get_non_null_fileds_exclude_extension():
            return []

        if filters.name:
            previews = self.__external_search_repository.search_by_name(filters)
        else:
            previews = self.__external_search_repository.search_by_filters(filters)

        if not previews:
            return []

        if user is not None:
            marked_previews = self.__set_already_added_flag_to_search_results(user, previews)
            return marked_previews

        return previews

    def add_to_unwatched(self, user: User, film_to_add: FilmExtended) -> None:
        self.__operations_repository.add_to_unwatched(user, film_to_add)

    def local_get(self, user: User,
                  film_to_get: FilmBase) -> FilmExtended:
        extended_film = self.__local_search_repository.get(user, film_to_get)
        if not extended_film:
            raise DoesNotExistException(film_to_get, user)

        return extended_film

    async def get(self, user: User, film_to_get: FilmPersonal) -> Union[FilmExtended, List[FilmExtended]]:
        extended_result = await local_search_wrapper(
            lambda: self.local_search_by_filters(
                user,
                BaseSearchingFilters(filmids=[film_to_get.filmid]),
                out_model=FilmTypes.FILM_EXTENDED
            )
        )

        if not extended_result:
            extended_result = await local_search_wrapper(
                lambda: self.local_search_by_filters(
                    None,
                    BaseSearchingFilters(filmids=[film_to_get.filmid]),
                    out_model=FilmTypes.FILM_EXTENDED
                )
            )

        if extended_result:
            return extended_result

        if film_to_get.is_series:
            seasons = self.__external_search_repository.get_seasons(
                BaseApiSearchingFilters(
                    filmid=film_to_get.filmid,
                    is_series=True
                )
            )

            if len(seasons) > 0:
                for season in seasons:
                    self.__series_to_film_policy.execute(season)

                asyncio.create_task(self.__operations_repository.cache(seasons))
                return seasons

            raise NotFoundExternalException(film_to_get)

        extended_film = self.__external_search_repository.get(film_to_get)
        asyncio.create_task(self.__operations_repository.cache(extended_film))
        if not extended_film:
            raise NotFoundExternalException(film_to_get)

        return extended_film

    def set_watch_status(self, user: User, film_to_set: FilmBase, status: bool) -> None:
        self.__operations_repository.set_watch_status(user, film_to_set, status)

    def set_rate(self, user: User, film_to_set: FilmBase, rating: BaseFilmComplexRating) -> None:
        self.__operations_repository.set_rate(user, film_to_set, rating)

    def remove(self, user: User, film_to_remove: FilmBase) -> None:
        self.__operations_repository.remove(user, film_to_remove)

    def get_list(self, user: User, is_watched: bool) -> List[FilmPreview]:
        target_list = self.__operations_repository.get_list(user, is_watched)
        if len(target_list) <= 0:
            raise EmptyListException(is_watched, user)

        return target_list

    def get_all(self, user: User) -> List[FilmPreview]:
        return self.__operations_repository.get_all(user)
