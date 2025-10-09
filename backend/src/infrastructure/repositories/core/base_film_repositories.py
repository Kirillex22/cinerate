from abc import abstractmethod
from typing import List, Optional, Union
from src.domain.entities.film import FilmPreview, FilmBase, FilmExtended, FilmTypes
from src.web.models.film_rating import BaseFilmComplexRating
from src.web.models.search_filters import BaseSearchingFilters, BaseApiSearchingFilters
from src.domain.entities.user import User


class BaseLocalSearchFilmRepository:
    @abstractmethod
    def search_by_filters(self, user: Optional[User], filters: BaseSearchingFilters,
                          out_model: FilmTypes = FilmTypes.FILM_PREVIEW) -> \
            Optional[
                Union[List[FilmPreview], List[FilmExtended]]]:
        pass

    @abstractmethod
    def get(self, user: User, film_to_get: FilmBase) -> Optional[FilmExtended]:
        pass


class BaseExternalSearchFilmRepository:
    @abstractmethod
    def search_by_filters(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        pass

    @abstractmethod
    def get(self, film_to_get: FilmBase) -> Optional[FilmExtended]:
        pass

    @abstractmethod
    def search_by_name(self, filters: BaseApiSearchingFilters) -> Optional[List[FilmPreview]]:
        pass

    @abstractmethod
    def get_seasons(self, filters: BaseApiSearchingFilters) -> List[FilmExtended]:
        pass


class BaseFilmOperationsRepository:
    @abstractmethod
    def _is_film_in_db(self, film_to_search: FilmBase) -> bool:
        pass

    @abstractmethod
    async def cache(self, film_to_cache: Union[FilmExtended, List[FilmExtended]]) -> None:
        pass

    @abstractmethod
    def add_to_unwatched(self, user: User, film_to_add: FilmExtended) -> None:
        pass

    @abstractmethod
    def set_watch_status(self, user: User, film_to_set: FilmBase, status: bool) -> None:
        pass

    @abstractmethod
    def set_rate(self, user: User, film_to_set: FilmBase, rating: BaseFilmComplexRating) -> None:
        pass

    @abstractmethod
    def remove(self, user: User, film_to_remove: FilmBase) -> None:
        pass

    @abstractmethod
    def get_list(self, user: User, is_watched: bool = True) -> List[FilmPreview]:
        pass

    @abstractmethod
    def get_all(self, user: User) -> List[FilmPreview]:
        pass
