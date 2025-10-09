from src.domain.entities.film import FilmBase
from src.domain.entities.user import User
from src.web.models.search_filters import BaseSearchingFilters, BaseApiSearchingFilters


class FilmServiceException(Exception):
    pass


class FilmIsNotSeriesException(FilmServiceException):
    code = "INVALID MODEL"

    def __init__(self, film: FilmBase):
        super().__init__(f"Film {film.filmid} is not a series")


class NotFoundLocalException(FilmServiceException):
    code = "NOT_FOUND"

    def __init__(self, filters: BaseSearchingFilters):
        super().__init__(f"Cannot find any film in your collection by filters: {filters}")


class NotFoundExternalException(FilmServiceException):
    code = "NOT_FOUND"

    def __init__(self, filters: BaseApiSearchingFilters):
        super().__init__(f"Cannot find any film in external search by filters: {filters}")


class EmptyListException(FilmServiceException):
    code = "EMPTY_LIST"

    def __init__(self, is_watched: bool, user: User):
        super().__init__(f"{'Watched' if is_watched else 'Watching'} list is empty for user {user.userid})")


class DoesNotExistException(FilmServiceException):
    code = "DOES_NOT_EXIST"

    def __init__(self, film: FilmBase, user: User):
        super().__init__(f"The film with id {film.filmid} does not exist for user {user.userid}")


class AlreadyWatchedException(FilmServiceException):
    code = "ALREADY_WATCHED"

    def __init__(self, film: FilmBase, user: User):
        super().__init__(f"The film with id {film.filmid} is already watched by user {user.userid}")


class AlreadyAddedException(FilmServiceException):
    code = "ALREADY_ADDED"

    def __init__(self, film: FilmBase, user: User):
        super().__init__(f"The film with id {film.filmid} already exists in user {user.userid} collection")


class MissingSearchFilterException(FilmServiceException):
    code = "MISSING_SEARCH_FILTER"

    def __init__(self, filters: BaseApiSearchingFilters):
        super().__init__(f"Missing required filter for search: {filters}")


class MissingGetFilterException(FilmServiceException):
    code = "MISSING_GET_FILTER"

    def __init__(self, filters: BaseApiSearchingFilters):
        super().__init__(f"Missing required filter (filmid) for get: {filters}")


class MissingSeasonsFilterException(FilmServiceException):
    code = "MISSING_SEASONS_FILTER"

    def __init__(self, filters: BaseApiSearchingFilters):
        super().__init__(f"Missing required filters (filmid and is_series=True) for seasons get: {filters}")
