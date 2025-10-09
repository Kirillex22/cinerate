from functools import wraps
from sqlmodel import Session, select
from typing import List, Optional, Union

from src.domain.entities.film import FilmPreview, FilmBase, FilmExtended, FilmTypes
from src.domain.entities.user import User
from src.infrastructure.repositories.impl.postgres.film_repository.tools.query_builders import LocalFilmSearchQueryBuilder
from src.infrastructure.repositories.core.base_film_repositories import BaseLocalSearchFilmRepository
from src.infrastructure.repositories.impl.postgres.film_repository.orm import Film, UserFilm
from src.shared.exceptions.base_exception_handler import BaseExceptionHandler
from src.web.models.search_filters import BaseSearchingFilters
from src.shared.mappers.orm_to_model import orm_join_to_film_extended, orm_join_to_film_preview, orm_to_film_preview, \
    orm_to_film_extended


def wrap_query(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)

        except Exception as e:
            film, user = None, None
            for arg in args:
                if isinstance(arg, FilmBase):
                    film = arg
                if isinstance(arg, User):
                    user = arg

            self._exception_handler.handle(e, film, user)

    return wrapper


class PostgresSearchFilmRepository(BaseLocalSearchFilmRepository):
    def __init__(self, session: Session, exception_handler: BaseExceptionHandler):
        self._exception_handler = exception_handler
        self._session = session

    @wrap_query
    def search_by_filters(self, user: Optional[User], filters: BaseSearchingFilters,
                          out_model: FilmTypes = FilmTypes.FILM_PREVIEW) -> Optional[
        Union[List[FilmPreview], List[FilmExtended]]]:

        if user is None:
            query = select(Film)
            builder = LocalFilmSearchQueryBuilder(query)
            query = builder.apply_all(filters).build()
            found_films_orm = self._session.exec(query).all()

            if out_model == FilmTypes.FILM_PREVIEW:
                found_films = [
                    orm_to_film_preview(film)
                    for film in found_films_orm
                ]

            elif out_model == FilmTypes.FILM_EXTENDED:
                found_films = [
                    orm_to_film_extended(film)
                    for film in found_films_orm
                ]

            else:
                found_films = []

        # ПОФИКСИТЬ ИМПОСТОРСКИЕ ФИЛЬМЫ
        else:
            userid = user.userid
            query = (
                select(UserFilm, Film)
                .select_from(Film)
                .outerjoin(UserFilm, (Film.filmid == UserFilm.filmid) & (UserFilm.userid == userid))
            )
            builder = LocalFilmSearchQueryBuilder(query)
            query = builder.apply_all(filters).build()
            found_films_orm = self._session.exec(query).all()

            if out_model == FilmTypes.FILM_PREVIEW:
                found_films = []
                for userfilm, film in found_films_orm:
                    if userfilm is not None:
                        found_films.append(orm_join_to_film_preview(userfilm, film))

            # нужно только для специфической ситуации
            elif out_model == FilmTypes.FILM_EXTENDED:
                found_films = []
                for userfilm, film in found_films_orm:
                    if userfilm is not None:
                        found_films.append(orm_join_to_film_extended(userfilm, film))
                    else:
                        found_films.append(orm_to_film_extended(film))

            else:
                found_films = []

        if len(found_films) > 0:
            return found_films

        return None

    @wrap_query
    def get(self, user: User, film_to_get: FilmBase) -> Optional[FilmExtended]:
        filmid, userid = film_to_get.filmid, user.userid

        query = select(UserFilm).join(Film).where(
            UserFilm.userid == userid).where(
            UserFilm.filmid == filmid)

        userfilm = next(self._session.exec(query), None)

        if not userfilm:
            query = select(Film).where(Film.filmid == filmid)
            film = next(self._session.exec(query), None)
            if not film:
                return None
            return film

        found_film = orm_join_to_film_extended(userfilm)

        return found_film
