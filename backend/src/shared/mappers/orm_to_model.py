from src.domain.entities.film import FilmPreview, FilmExtended, Episode
from src.domain.entities.playlist import Playlist, PlaylistItem, PlaylistItemPreview
from src.domain.entities.user import UserPublic, User, UserPreview, RoleEnum, StatusEnum, UserHistoryModel, UserInDb
from src.infrastructure.repositories.impl.postgres.film_repository.orm import Film, UserFilm
from src.infrastructure.repositories.impl.postgres.playlist_repository.orm import PlaylistORM, PlaylistItemORM
from src.infrastructure.repositories.impl.postgres.social_repository.orm import UserORM
from src.web.models.search_filters import SearchingFiltersWithUserData


def orm_join_to_film_preview(userfilm: UserFilm, film: Film) -> FilmPreview:
    # film = userfilm.film
    return FilmPreview(
        filmid=film.filmid,
        name=film.name,
        poster_link=film.poster_link,
        release_year=film.release_year,
        alternative_name=film.alternative_name,
        genres=film.genres,
        countries=film.countries,
        director=film.director,
        time_minutes=film.time_minutes,
        age_rating=film.age_rating,

        # userfilm data:
        is_series=film.is_series,
        season=userfilm.film.season,
        already_added=True,
        is_watched=userfilm.is_watched,
        user_rating=userfilm.user_rating,
        last_updated=film.last_updated,
        added_at=userfilm.added_at
    )


def orm_to_film_preview(film: Film) -> FilmPreview:
    return FilmPreview(
        filmid=film.filmid,
        name=film.name,
        poster_link=film.poster_link,
        release_year=film.release_year,
        is_series=film.is_series,
        alternative_name=film.alternative_name,
        genres=film.genres,
        countries=film.countries,
        director=film.director,
        time_minutes=film.time_minutes,
        age_rating=film.age_rating,
        last_updated=film.last_updated,
        season=film.season
    )


def orm_to_film_extended(film: Film) -> FilmExtended:
    return FilmExtended(
        filmid=film.filmid,
        name=film.name,
        is_series=film.is_series,
        season=film.season,
        poster_link=film.poster_link,
        last_updated=film.last_updated,
        alternative_name=film.alternative_name,
        release_year=film.release_year,
        genres=film.genres,
        slogan=film.slogan,
        countries=film.countries,
        director=film.director,
        description=film.description,
        age_rating=film.age_rating,
        persons=film.persons,
        time_minutes=film.time_minutes,
        ratings=film.ratings,
        trailers=film.trailers,
        end_year=film.end_year,
        status=film.status,
        tops=film.tops,
        episodes=[Episode(**episode) for episode in film.episodes] if film.episodes else []
    )


def orm_to_playlist(orm: PlaylistORM) -> Playlist:
    return Playlist(
        userid=str(orm.userid),
        playlistid=str(orm.playlistid),
        name=orm.name,
        description=orm.description,
        is_public=orm.is_public,
        additions_count=orm.additions_count,
        gen_attrs=SearchingFiltersWithUserData(**orm.gen_attrs) if orm.gen_attrs else None,
        collaborators=orm.collaborators,
    )


def orm_to_playlist_item(orm: PlaylistItemORM) -> PlaylistItem:
    return PlaylistItem(
        playlistid=str(orm.playlistid),
        filmid=orm.filmid,
        creatorid=str(orm.creatorid),
    )


def orm_to_playlist_item_preview(orm: PlaylistItemORM) -> PlaylistItemPreview:
    return PlaylistItemPreview(
        item=PlaylistItem(
            playlistid=str(orm.playlistid),
            filmid=orm.filmid,
            creatorid=str(orm.creatorid)
        ),
        preview=orm_to_film_preview(orm.film)
    )


def orm_join_to_film_extended(userfilm: UserFilm, film: Film) -> FilmExtended:
    # film = userfilm.film
    return FilmExtended(
        filmid=film.filmid,
        name=film.name,
        is_series=film.is_series,
        season=film.season,
        poster_link=film.poster_link,
        last_updated=film.last_updated,
        alternative_name=film.alternative_name,
        release_year=film.release_year,
        genres=film.genres,
        slogan=film.slogan,
        countries=film.countries,
        director=film.director,
        description=film.description,
        age_rating=film.age_rating,
        persons=film.persons,
        time_minutes=film.time_minutes,
        ratings=film.ratings,
        trailers=film.trailers,
        end_year=film.end_year,
        status=film.status,
        tops=film.tops,
        episodes=[Episode(**episode) for episode in film.episodes] if film.episodes else [],

        # userfilm data:
        is_watched=userfilm.is_watched,
        user_rating=userfilm.user_rating,
        added_at=userfilm.added_at,
        already_added=True
    )


def orm_join_to_user_public(result: dict) -> UserPublic:
    upd_result = orm_join_helper(result)
    return UserPublic(**upd_result)


def orm_join_to_user(result: dict) -> User:
    upd_result = orm_join_helper(result)
    return User(**upd_result)


def orm_join_to_user_preview(result: dict) -> UserPreview:
    upd_result = orm_join_helper(result)
    return UserPreview(**upd_result)


def orm_join_helper(result: dict) -> dict:
    # user_
    if result.get('id'):
        result['userid'] = str(result.pop('id'))
    if result.get('item_id'):
        result['item_id'] = str(result['item_id'])
    if result.get('role'):
        result['role'] = RoleEnum[result['role']].value
    if result.get('status'):
        result['status'] = StatusEnum[result['status']].value
    # orm_join_to_user_history
    # есть users_actions_history.uah_id а есть actions.action_id
    # if result.get('action_id'):
    #     result['aid'] = str(result.pop('action_id'))
    if result.get('uah_id'):
        result['aid'] = str(result.pop('uah_id'))
    if result.get('user_id'):
        result['uid'] = str(result.pop('user_id'))

    return result


def orm_join_to_user_history(result: dict) -> UserHistoryModel:
    upd_result = orm_join_helper(result)
    return UserHistoryModel(**upd_result)


def user_orm_to_user_in_db(user: UserORM) -> UserInDb:
    return UserInDb(userid=str(user.id), login=user.login, hashed_password=user.hashed_password,
                    role=RoleEnum[user.user_item.role])
