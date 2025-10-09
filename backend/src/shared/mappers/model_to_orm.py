from datetime import datetime
import uuid
from src.domain.entities.film import FilmExtended, FilmBase
from src.domain.entities.playlist import Playlist, PlaylistItem
from src.domain.entities.user import User
from src.web.models.playlists import CreatePlaylistModel, PlaylistSearchFilters
from src.infrastructure.repositories.impl.postgres.film_repository.orm import Film, UserFilm
from src.infrastructure.repositories.impl.postgres.playlist_repository.orm import PlaylistORM, PlaylistItemORM


def film_extended_to_film_orm(film: FilmExtended, serialize_for_json) -> Film:
    return Film(
        **film.model_dump(exclude={"persons", "episodes", "poster_link", "is_series", "last_updated"}),
        poster_link=str(film.poster_link) if film.poster_link else None,
        is_series=film.is_series or False,
        last_updated=film.last_updated or datetime.now(),
        persons=serialize_for_json(film.persons) if film.persons else None,
        episodes=serialize_for_json(film.episodes) if film.episodes else None,
    )


def film_base_to_userfilm_orm(film: FilmBase, user: User, serialize_for_json) -> UserFilm:
    return UserFilm(
        filmid=film.filmid,
        userid=uuid.UUID(user.userid),
        is_watched=film.is_watched if film.is_watched else False,
        user_rating=serialize_for_json(film.user_rating) if film.user_rating else None,
        added_at=film.added_at,
        already_added=film.already_added if film.already_added else None
    )


def user_and_create_model_to_playlist_orm(user: User, create_model: CreatePlaylistModel) -> PlaylistORM:
    return PlaylistORM(
        userid=uuid.UUID(user.userid),
        description=create_model.description,
        name=create_model.name,
        is_public=create_model.is_public if create_model.is_public else False,
        gen_attrs=create_model.gen_attrs.model_dump() if create_model.gen_attrs else None,
        collaborators=[]
    )


def filters_film_user_to_playlist_item_orm(filters: PlaylistSearchFilters, film: FilmBase,
                                           user: User) -> PlaylistItemORM:
    return PlaylistItemORM(
        playlistid=uuid.UUID(filters.playlistid),
        filmid=film.filmid,
        creatorid=user.userid,
    )


def playlist_to_orm(model: Playlist) -> PlaylistORM:
    return PlaylistORM(
        userid=uuid.UUID(model.userid),
        playlistid=uuid.UUID(model.playlistid),
        name=model.name,
        description=model.description,
        is_public=model.is_public,
        additions_count=model.additions_count,
        gen_attrs=model.gen_attrs,
        collaborators=model.collaborators or [],
    )


def playlist_item_to_orm(model: PlaylistItem) -> PlaylistItemORM:
    return PlaylistItemORM(
        playlistid=uuid.UUID(model.playlistid),
        filmid=model.filmid,
        creatorid=model.creatorid,
    )
