import jwt
from sqlmodel import Session
from fastapi import Depends, HTTPException, Cookie, status
from passlib.context import CryptContext
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.domain.entities.user import User
from src.domain.policies.impl.kp_series_to_film import DefaultSeriesToFilmPolicy
from src.services.film.service import FilmService
from src.services.playlist.service import PlaylistService
from src.services.social.service import SocialService
from src.infrastructure.factories.api import API
from src.infrastructure.repositories.impl.postgres.film_repository.external_search_film_repository import KpApiSearchFilmRepository
from src.infrastructure.repositories.impl.postgres.film_repository.local_search_film_repository import PostgresSearchFilmRepository
from src.infrastructure.repositories.impl.postgres.film_repository.operations_film_repository import PostgresFilmOperationsRepository
from src.infrastructure.repositories.impl.postgres.playlist_repository.playlist_repository import PostgresPlaylistRepository
from src.infrastructure.repositories.impl.postgres.social_repository.social_repository import PostgresSocialRepository
from src.services.auth.service import AuthService
from src.infrastructure.repositories.shared.orm.sqlmodel_exception_handler import SQLModelExceptionHandler
from src.web.models.playlists import AccessModel as PlaylistAccessModel
from src.web.models.users import AccessModel as UserAccessModel
from src.infrastructure.factories.database import Database
from src.config.settings import AppSettings

app_settings = AppSettings().from_yaml()
pg_client = Database(app_settings, False)
api_client = API(app_settings)

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
session_dep: Session = Depends(pg_client.get_session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Инициализация схемы БД...')
    pg_client.init_db()
    print('Схема БД инициализирована.')

    local_session = next(pg_client.get_session())
    repo = PostgresSocialRepository(session=local_session)
    auth_service = AuthService(
        app_settings.SECURITY_SETTINGS,
        repo,
        crypt_context
    )
    try:
        if not repo.get_user(None, app_settings.ADMIN_USER.login):
            auth_service.register_user(app_settings.ADMIN_USER, is_admin=True)
            print('Администратор из конфигурации добавлен.')
    except Exception as e:
        print(e)
        pass
    local_session.close()
    yield
    print("💥 Shutdown")


def get_auth_service_dep(session: Session = session_dep) -> AuthService:
    return AuthService(
        security_config=app_settings.SECURITY_SETTINGS,
        social_repository=PostgresSocialRepository(session),
        pwd_context=crypt_context
    )


def get_social_service_dep(session: Session = session_dep) -> SocialService:
    return SocialService(
        repository=PostgresSocialRepository(
            session=session
        )
    )


def get_film_service_dep(session: Session = session_dep) -> FilmService:
    return FilmService(
        local_search_repository=PostgresSearchFilmRepository(session, SQLModelExceptionHandler()),
        external_search_repository=KpApiSearchFilmRepository(api_client.get_client()),
        operations_repository=PostgresFilmOperationsRepository(session,
                                                               SQLModelExceptionHandler()),
        series_to_film_policy=DefaultSeriesToFilmPolicy()
    )


def get_playlist_service_dep(session: Session = session_dep) -> PlaylistService:
    return PlaylistService(
        repository=PostgresPlaylistRepository(
            session=session,
            film_search_repository=PostgresSearchFilmRepository(
                session,
                SQLModelExceptionHandler()
            )
        )
    )


def get_current_user(
        access_token: str = Cookie(None),
        auth_service: AuthService = Depends(get_auth_service_dep)
) -> User:
    if access_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing access token')
    try:
        user = auth_service.get_user_by_access_token(access_token)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")


def build_access_model(current_user: User) -> PlaylistAccessModel:
    return PlaylistAccessModel(current_user=current_user)


def build_user_access_model(current_user: User) -> UserAccessModel:
    return UserAccessModel(current_user=current_user)
