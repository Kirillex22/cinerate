import uuid
from functools import wraps
from typing import Optional, Union, List

from sqlmodel import Session, select

from src.infrastructure.repositories.core.base_film_repositories import BaseLocalSearchFilmRepository
from src.infrastructure.repositories.core.base_playlist_repository import BasePlaylistRepository
from src.domain.entities.film import FilmBase
from src.domain.entities.playlist import Playlist, PlaylistItemPreview, PlaylistItem
from src.domain.entities.user import User
from src.web.models.playlists import PlaylistSearchFilters, CreatePlaylistModel
from src.shared.mappers.model_to_orm import user_and_create_model_to_playlist_orm, \
    filters_film_user_to_playlist_item_orm
from src.shared.mappers.orm_to_model import orm_to_playlist, orm_to_playlist_item, orm_to_playlist_item_preview
from src.infrastructure.repositories.impl.postgres.playlist_repository.orm import PlaylistORM
from src.infrastructure.repositories.impl.postgres.playlist_repository.tools.query_builders import PlaylistQueryBuilder


def wrap_query(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            func_result = func(self, *args, **kwargs)
            self._session.commit()
            return func_result

        except Exception as e:
            self._session.rollback()
            raise e

    return wrapper


class PostgresPlaylistRepository(BasePlaylistRepository):
    def __init__(self, session: Session, film_search_repository: BaseLocalSearchFilmRepository):
        self._session = session
        self._film_search_repository = film_search_repository

    @wrap_query
    def create_playlist(self, user: User, create_model: CreatePlaylistModel) -> str:
        playlist_orm = user_and_create_model_to_playlist_orm(user, create_model)
        self._session.add(playlist_orm)
        self._session.flush()
        return str(playlist_orm.playlistid)

    @wrap_query
    def autofill_playlist(self,
                          filters: PlaylistSearchFilters) -> None:  # нужно передать в фильтрах id плейлиста, а также целевого пользователя (текущего)
        playlist_orm: PlaylistORM = self._session.get(PlaylistORM, uuid.UUID(filters.playlistid))
        film_filters = orm_to_playlist(playlist_orm).gen_attrs

        if playlist_orm:
            film_ids_to_exclude = [item.filmid for item in playlist_orm.items]
            films_by_filters = self._film_search_repository.search_by_filters(filters.target_user, film_filters)

            if not films_by_filters:
                return
            for film in films_by_filters:
                if film.filmid not in film_ids_to_exclude:
                    self.add_to_playlist(filters, film, filters.target_user)

    @wrap_query
    def get_playlists(self, filters: PlaylistSearchFilters) -> Optional[
        Union[List[Playlist], Playlist]]:
        query = select(PlaylistORM)
        builder = PlaylistQueryBuilder(query)
        query = builder.apply_all(filters).build()

        playlists_orm = self._session.exec(query).all()

        if len(playlists_orm) == 0:
            return None

        if len(playlists_orm) == 1:
            model = orm_to_playlist(playlists_orm[0])
            return model

        models = [orm_to_playlist(playlist_orm) for playlist_orm in playlists_orm]

        return models

    @wrap_query
    def remove_playlist(self, filters: PlaylistSearchFilters) -> None:
        query = select(PlaylistORM)
        builder = PlaylistQueryBuilder(query)
        query = builder.apply_all(filters).build()

        playlist_orm = self._session.exec(query).first()
        self._session.delete(playlist_orm)

    @wrap_query
    def add_to_playlist(self, filters: PlaylistSearchFilters, film_to_add: FilmBase, contributor: User) -> None:
        playlist_item_orm = filters_film_user_to_playlist_item_orm(filters, film_to_add, contributor)
        self._session.add(playlist_item_orm)

    @wrap_query
    def get_playlist_item(self, filters: PlaylistSearchFilters, film_to_get: FilmBase) -> Optional[PlaylistItem]:
        filmid = film_to_get.filmid

        query = select(PlaylistORM)
        builder = PlaylistQueryBuilder(query)
        query = builder.apply_all(filters).build()

        playlist_orm: PlaylistORM = self._session.exec(query).first()
        playlist_item_orm = next((item for item in playlist_orm.items if item.filmid == filmid), None)
        playlist_item = orm_to_playlist_item(playlist_item_orm)

        return playlist_item

    @wrap_query
    def remove_playlist_item(self, filters: PlaylistSearchFilters, film_to_remove: FilmBase) -> None:
        filmid = film_to_remove.filmid

        query = select(PlaylistORM)
        builder = PlaylistQueryBuilder(query)
        query = builder.apply_all(filters).build()

        playlist_orm: PlaylistORM = self._session.exec(query).first()
        playlist_item_orm = next((item for item in playlist_orm.items if item.filmid == filmid), None)
        self._session.delete(playlist_item_orm)

    @wrap_query
    def update_playlist(self, playlist: Playlist) -> None:
        query = select(PlaylistORM).where(
            (PlaylistORM.playlistid == playlist.playlistid) & (PlaylistORM.userid == playlist.userid))
        playlist_orm: PlaylistORM = self._session.exec(query).first()

        custom_attributes = playlist.get_custom_non_null_fields()
        playlist_orm.update_playlist_orm_from_model(custom_attributes)

    @wrap_query
    def get_playlist_content(self, filters: PlaylistSearchFilters) -> Optional[List[PlaylistItemPreview]]:
        query = select(PlaylistORM)
        builder = PlaylistQueryBuilder(query)
        query = builder.apply_all(filters).build()

        playlist_orm: PlaylistORM = self._session.exec(query).first()
        playlist_items = [orm_to_playlist_item_preview(playlist_item_orm) for playlist_item_orm in playlist_orm.items]

        if len(playlist_items) == 0:
            return None

        return playlist_items

    @wrap_query
    def get_playlist_by_id(self, playlistid: str) -> Optional[Playlist]:
        playlist_orm: PlaylistORM = self._session.get(PlaylistORM, uuid.UUID(playlistid))
        if playlist_orm:
            return orm_to_playlist(playlist_orm)
        return None
