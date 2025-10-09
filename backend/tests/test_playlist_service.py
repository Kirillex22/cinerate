from datetime import datetime

import pytest
from sqlmodel import SQLModel
from sqlalchemy import text

from src.domain.entities.playlist import Playlist
from src.services.playlist.service import PlaylistService
from src.domain.entities.user import User
from src.domain.entities.film import FilmExtended, Person, Episode, FilmPreview
from src.infrastructure.repositories.impl import PostgresSearchFilmRepository
from src.infrastructure.repositories.shared.orm.sqlmodel_exception_handler import SQLModelExceptionHandler
from src.web.models.playlists import CreatePlaylistModel, PlaylistSearchFilters, AccessModel
from src.shared.mappers.model_to_orm import film_extended_to_film_orm
from src.infrastructure.repositories.impl.postgres.film_repository.tools.postgres_json_serializer import serialize_for_json
from src.infrastructure.repositories.impl.postgres.playlist_repository.playlist_repository import PostgresPlaylistRepository
from src.services.playlist.exceptions import PlaylistsNotFoundException, \
    UserDoesntHavePermissionException, EmptyPlaylistException
from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale
from tests.test_film_service import get_session


@pytest.fixture
def sample_film(get_session) -> FilmExtended:
    film = FilmExtended(
        filmid="tt1234567",
        season=2,
        name="Example Film",
        poster_link="https://example.com/poster.jpg",
        release_year=2023,
        is_series=True,
        alternative_name="Example Alt Name",
        genres=["Drama", "Thriller"],
        slogan="An unforgettable journey",
        countries=["USA", "UK"],
        director="John Doe",
        description="A powerful film about transformation and identity.",
        persons=[
            Person(id=1, name="Actor One", photo="https://example.com/actor1.jpg", en_profession="actor"),
            Person(id=2, name="Director One", en_profession="director")
        ],
        time_minutes=120,
        ratings={"imdb": 7.8, "kinopoisk": 8.1},
        trailers=["https://youtube.com/trailer1", "https://youtube.com/trailer2"],
        end_year=2023,
        status="released",
        tops=["top250", "user_choice"],
        last_updated=datetime.now(),
        episodes=[
            Episode(number=1, name="Pilot", air_date=datetime(2023, 1, 1)),
            Episode(number=2, name="Next Step", air_date=datetime(2023, 1, 8))
        ],
        user_rating=BaseFilmComplexRating[BaseRatingScale](
            storyline=BaseRatingScale.GOOD,
            music=BaseRatingScale.NORMAL,
            camera_work=BaseRatingScale.AWESOME,
            acting_game=BaseRatingScale.AWESOME
        ),
        added_at=datetime.now(),
    )
    film = film_extended_to_film_orm(film, serialize_for_json=serialize_for_json)
    get_session.add(film)
    get_session.commit()
    get_session.refresh(film)
    return film


@pytest.fixture
def sample_user_1():
    return User(userid="user1", role=1)


@pytest.fixture
def sample_user_2():
    return User(userid="user2", role=1)


@pytest.fixture
def create_playlist_model():
    return CreatePlaylistModel(
        name="Test Playlist",
        is_public=False,
        description="Test Desc",
        collaborators=[],
        gen_attrs=None
    )


@pytest.fixture
def playlist_service(get_session):
    sub_repo = PostgresSearchFilmRepository(get_session, SQLModelExceptionHandler())
    repo = PostgresPlaylistRepository(get_session, sub_repo)
    return PlaylistService(repo)


@pytest.fixture
def filters_for_playlist(sample_user_1):
    return PlaylistSearchFilters(
        playlistid=1,
        target_user=sample_user_1
    )


@pytest.fixture(autouse=True)
def clean_db(get_session):
    for table in reversed(list(SQLModel.metadata.sorted_tables)):
        get_session.exec(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
    get_session.commit()


def test_create_and_get_and_remove_playlist(playlist_service, sample_user_1, create_playlist_model):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist = playlist_service.get_playlists(filters, access)

    assert isinstance(playlist, Playlist)
    assert playlist.name == "Test Playlist"

    access = AccessModel(current_user=sample_user_1)
    playlist_service.remove_playlist(access, filters)

    with pytest.raises(PlaylistsNotFoundException):
        playlist_service.get_playlists(filters, access)


def test_add_and_remove_film(playlist_service, sample_user_1, sample_film, create_playlist_model):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.add_to_playlist(access, filters, sample_film)

    content = playlist_service.get_playlist_content(access, filters)

    assert content[0].preview == FilmPreview(**sample_film.model_dump())

    playlist_service.remove_from_playlist(access, filters, sample_film)

    with pytest.raises(EmptyPlaylistException):
        playlist_service.get_playlist_content(access, filters)


def test_set_publicity(playlist_service, sample_user_1, sample_user_2, create_playlist_model):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)
    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.set_publicity(access, filters, True)
    updated = playlist_service.get_playlists(filters, access)

    assert updated.is_public is True

    access = AccessModel(current_user=sample_user_2)

    # если не найдет, то бросит исключение и тест завалится
    playlist_service.get_playlists(filters, access)


def test_try_get_non_public_playlist(playlist_service, sample_user_1, sample_user_2, create_playlist_model):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(PlaylistsNotFoundException):
        playlist_service.get_playlists(filters, access)


def test_add_collaborator_and_let_him_add_film(playlist_service, sample_user_1, sample_user_2, create_playlist_model,
                                               sample_film):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.add_collaborator(access, filters, sample_user_2)
    playlist = playlist_service.get_playlists(filters, access)

    assert sample_user_2.userid in playlist.collaborators

    access = AccessModel(current_user=sample_user_2)

    playlist_service.add_to_playlist(access, filters, sample_film)


def test_add_film_being_not_collaborator_to_public_playlist(playlist_service, sample_user_1, sample_user_2,
                                                            create_playlist_model, sample_film):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.set_publicity(access, filters, True)

    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(UserDoesntHavePermissionException) as e:
        playlist_service.add_to_playlist(access, filters, sample_film)

    assert 'add' in str(e.value)


def test_search_private_playlist(playlist_service, sample_user_1, sample_user_2,
                                 create_playlist_model):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(PlaylistsNotFoundException):
        playlist_service.get_playlists(filters, access)


def test_delete_creator_film_from_playlist_being_not_creator(playlist_service, sample_user_1, sample_user_2,
                                                             create_playlist_model, sample_film):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.add_to_playlist(access, filters, sample_film)

    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(UserDoesntHavePermissionException) as e:
        playlist_service.remove_from_playlist(access, filters, sample_film)

    assert 'remove film' in str(e.value)


def test_delete_other_collaborator_film_from_playlist(playlist_service, sample_user_1, sample_user_2,
                                                      create_playlist_model, sample_film):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.add_to_playlist(access, filters, sample_film)
    playlist_service.add_collaborator(access, filters, sample_user_2)

    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(UserDoesntHavePermissionException) as e:
        playlist_service.remove_from_playlist(access, filters, sample_film)

    assert 'remove film' in str(e.value)


def test_delete_other_collaborator_from_playlist(playlist_service, sample_user_1, sample_user_2, create_playlist_model):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.add_collaborator(access, filters, sample_user_2)

    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(UserDoesntHavePermissionException) as e:
        playlist_service.remove_from_collaborators(access, filters, sample_user_1)

    assert 'remove collaborator' in str(e.value)


def test_add_film_to_playlist_and_remove_film_from_main_list(playlist_service, sample_user_1, create_playlist_model,
                                                             sample_film, get_session):
    pid = playlist_service.create_playlist(sample_user_1, create_playlist_model)

    filters = PlaylistSearchFilters(playlistid=pid)
    access = AccessModel(current_user=sample_user_1)

    playlist_service.add_to_playlist(access, filters, sample_film)
    get_session.delete(sample_film)

    with pytest.raises(EmptyPlaylistException):
        playlist_service.get_playlist_content(access, filters)


def test_get_user_playlists(playlist_service, sample_user_1, sample_user_2, create_playlist_model):
    playlist_service.create_playlist(sample_user_1, create_playlist_model)
    filters = PlaylistSearchFilters(target_user=sample_user_1)
    access = AccessModel(current_user=sample_user_2)

    with pytest.raises(PlaylistsNotFoundException):
        playlist_service.get_playlists(filters, access)
