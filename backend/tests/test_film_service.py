import pytest
from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

from src.config.settings import AppSettings
from src.domain.entities.film import FilmExtended, Person, Episode
from src.domain.policies.impl.kp_series_to_film import DefaultSeriesToFilmPolicy
from src.infrastructure.repositories.impl.postgres.film_repository.external_search_film_repository import KpApiSearchFilmRepository
from src.infrastructure.repositories.impl import PostgresSearchFilmRepository
from src.infrastructure.repositories.impl.postgres.film_repository.operations_film_repository import PostgresFilmOperationsRepository
from src.infrastructure.repositories.shared.orm.sqlmodel_exception_handler import SQLModelExceptionHandler
from src.services.film.service import FilmService
from src.shared.tools.api_clients.core.base_external_api_client import BaseExternalAPIClient
from src.domain.entities.user import User
from src.services.film.exceptions import NotFoundLocalException, DoesNotExistException
from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale
from src.web.models.search_filters import BaseSearchingFilters

app_settings = AppSettings().from_yaml()
DATABASE_URL = app_settings.POSTGRES_SETTINGS.make_url()
engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def create_all():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def get_session():
    with Session(engine, expire_on_commit=False) as session:
        for table in SQLModel.metadata.tables.values():
            session.exec(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
        session.commit()

        yield session


@pytest.fixture
def sample_film():
    return FilmExtended(
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


@pytest.fixture
def sample_user():
    return User(userid="user1", role=1)


@pytest.fixture
def sample_rating():
    return BaseFilmComplexRating[BaseRatingScale](
        storyline=BaseRatingScale.NORMAL,
        music=BaseRatingScale.NORMAL,
        camera_work=BaseRatingScale.NORMAL,
        acting_game=BaseRatingScale.NORMAL
    )


@pytest.fixture
def film_service(get_session):
    repo = PostgresSearchFilmRepository(get_session, SQLModelExceptionHandler())
    ops = PostgresFilmOperationsRepository(get_session, SQLModelExceptionHandler())
    return FilmService(
        local_search_repository=repo,
        external_search_repository=KpApiSearchFilmRepository(BaseExternalAPIClient()),
        operations_repository=ops,
        series_to_film_policy=DefaultSeriesToFilmPolicy()
    )


def test_add_and_get_film(film_service, sample_user, sample_film):
    film_service.add_to_unwatched(sample_user, sample_film)
    fetched = film_service.local_get(sample_user, sample_film)
    assert fetched.filmid == sample_film.filmid


def test_set_watched(film_service, sample_user, sample_film):
    film_service.add_to_unwatched(sample_user, sample_film)
    film_service.set_watch_status(sample_user, sample_film, True)
    watched = film_service.get_list(sample_user, is_watched=True)
    assert any(f.filmid == sample_film.filmid for f in watched)


def test_set_rating(film_service, sample_user, sample_film, sample_rating):
    film_service.add_to_unwatched(sample_user, sample_film)
    film_service.set_rate(sample_user, sample_film, sample_rating)
    rated = film_service.local_get(sample_user, sample_film)
    assert rated.user_rating.storyline == sample_rating.storyline


def test_remove_film(film_service, sample_user, sample_film):
    film_service.add_to_unwatched(sample_user, sample_film)
    film_service.remove(sample_user, sample_film)


def test_search_by_filters(film_service, sample_user, sample_film):
    film_service.add_to_unwatched(sample_user, sample_film)
    filters = BaseSearchingFilters(filmid=sample_film.filmid)
    result = film_service.local_search_by_filters(sample_user, filters)
    assert isinstance(result, list)


def test_get_all(film_service, sample_user):
    all_films = film_service.get_all(sample_user)
    assert isinstance(all_films, list)


def test_search_by_filters_unexisting(film_service, sample_user, sample_film):
    filters = BaseSearchingFilters(filmid=sample_film.filmid)
    with pytest.raises(NotFoundLocalException): film_service.local_search_by_filters(sample_user, filters)


def test_set_rating_unexisting(film_service, sample_user, sample_film, sample_rating):
    with pytest.raises(DoesNotExistException):
        film_service.set_rate(sample_user, sample_film, sample_rating)
