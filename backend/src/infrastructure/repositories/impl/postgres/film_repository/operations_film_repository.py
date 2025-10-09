import traceback
from functools import wraps
from sqlmodel import Session, select
from typing import List, Union

from src.shared.mappers.model_to_orm import film_extended_to_film_orm, film_base_to_userfilm_orm
from src.shared.mappers.orm_to_model import orm_join_to_film_preview
from src.domain.entities.film import FilmPreview, FilmBase, FilmExtended
from src.domain.entities.user import User
from src.infrastructure.repositories.impl.postgres.film_repository.tools.postgres_json_serializer import serialize_for_json
from src.web.models.film_rating import BaseFilmComplexRating
from src.infrastructure.repositories.core.base_film_repositories import BaseFilmOperationsRepository
from src.infrastructure.repositories.impl.postgres.film_repository.orm import Film, UserFilm
from src.shared.exceptions.base_exception_handler import BaseExceptionHandler
from src.services.film.exceptions import DoesNotExistException


def wrap_query(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            self._session.commit()
            return result
        except Exception as e:
            self._session.rollback()
            film, user = None, None
            for arg in args:
                if isinstance(arg, FilmBase):
                    film = arg
                if isinstance(arg, User):
                    user = arg
            self._exception_handler.handle(e, film, user)

    return wrapper


class PostgresFilmOperationsRepository(BaseFilmOperationsRepository):
    def __init__(self, session: Session, exception_handler: BaseExceptionHandler):
        self._exception_handler = exception_handler
        self._session = session

    @wrap_query
    def _is_film_in_db(self, film_to_search: FilmBase) -> bool:
        filmid = film_to_search.filmid
        found_film = self._session.get(Film, filmid)

        if found_film:
            return True

        return False

    @wrap_query
    def _cache_one(self, film_to_cache: FilmExtended) -> None:
        if not self._is_film_in_db(film_to_cache):
            orm_to_add = film_extended_to_film_orm(film_to_cache, serialize_for_json=serialize_for_json)
            self._session.add(orm_to_add)

    async def cache(self, film_to_cache: Union[FilmExtended, List[FilmExtended]]) -> None:
        if isinstance(film_to_cache, FilmExtended):
            self._cache_one(film_to_cache)

        raised_exceptions = []

        if isinstance(film_to_cache, list):
            orms_to_add = [film_extended_to_film_orm(film_extended, serialize_for_json=serialize_for_json) for
                           film_extended in film_to_cache]
            for orm in orms_to_add:
                try:
                    self._cache_one(orm)
                except:
                    raised_exceptions.append(traceback.format_exc())

        if raised_exceptions:
            all_errors = "\n\n".join(raised_exceptions)
            raise Exception(f"Ошибки при добавлении сезонов:\n{all_errors}")

    @wrap_query
    def add_to_unwatched(self, user: User, film_to_add: FilmExtended) -> None:
        orm_to_add = film_base_to_userfilm_orm(film_to_add, user, serialize_for_json=serialize_for_json)
        self._session.add(orm_to_add)

    @wrap_query
    def set_watch_status(self, user: User, film_to_set: FilmBase, status: bool) -> None:
        userid, filmid = user.userid, film_to_set.filmid

        orm_to_watch: UserFilm = self._session.exec(
            select(UserFilm).where(UserFilm.userid == userid).where(UserFilm.filmid == filmid)
        ).first()

        if not orm_to_watch:
            raise DoesNotExistException(film_to_set, user)

        orm_to_watch.set_watch_status(status)

    @wrap_query
    def set_rate(self, user: User, film_to_set: FilmBase, rating: BaseFilmComplexRating) -> None:
        userid, filmid = user.userid, film_to_set.filmid

        orm_to_rate = self._session.exec(
            select(UserFilm).where(UserFilm.userid == userid).where(UserFilm.filmid == filmid)
        ).first()

        if not orm_to_rate:
            raise DoesNotExistException(film_to_set, user)

        orm_to_rate.set_rating(rating, serialize_for_json=serialize_for_json)

    @wrap_query
    def remove(self, user: User, film_to_remove: FilmBase) -> None:
        userid, filmid = user.userid, film_to_remove.filmid

        orm_to_remove = self._session.exec(
            select(UserFilm).where(UserFilm.userid == userid).where(UserFilm.filmid == filmid)).first()

        if not orm_to_remove:
            raise DoesNotExistException(film_to_remove, user)

        self._session.delete(orm_to_remove)

    @wrap_query
    def get_list(self, user: User, is_watched: bool = True) -> List[FilmPreview]:
        userid = user.userid

        found_films = self._session.exec(
            select(UserFilm).where(UserFilm.userid == userid).where(
                UserFilm.is_watched == is_watched)
        ).all()

        target_list = [orm_join_to_film_preview(userfilm, userfilm.film) for userfilm in found_films]
        return target_list

    @wrap_query
    def get_all(self, user: User) -> List[FilmPreview]:
        userid = user.userid

        found_films = self._session.exec(
            select(UserFilm).where(UserFilm.userid == userid)
        ).all()

        target_list = [orm_join_to_film_preview(userfilm, userfilm.film) for userfilm in found_films]
        return target_list
