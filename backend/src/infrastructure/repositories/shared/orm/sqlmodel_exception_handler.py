from typing import Optional

from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
    OperationalError,
    ProgrammingError,
    NoResultFound,
    MultipleResultsFound,
    PendingRollbackError,
    StatementError,
    DBAPIError,
)

from src.domain.entities.film import FilmBase
from src.domain.entities.user import User
from src.shared.exceptions.base_exception_handler import BaseExceptionHandler
from src.services.film.exceptions import AlreadyAddedException


class SQLModelExceptionHandler(BaseExceptionHandler):
    def handle(self, exc: Exception, film: Optional[FilmBase] = None, user: Optional[User] = None) -> None:
        if not film:
            film = FilmBase(filmid='None')
        if not user:
            user = User(userid='None')

        if isinstance(exc, IntegrityError):
            raise AlreadyAddedException(film, user)
        elif isinstance(exc, NoResultFound):
            raise LookupError("Запись не найдена в базе данных.")
        elif isinstance(exc, MultipleResultsFound):
            raise LookupError("Ожидалась одна запись, но найдено несколько.")
        elif isinstance(exc, OperationalError):
            raise ConnectionError("Проблема с подключением к базе данных.")
        elif isinstance(exc, ProgrammingError):
            raise RuntimeError("Ошибка в SQL-запросе или схеме.")
        elif isinstance(exc, PendingRollbackError):
            raise RuntimeError("Операция невозможна: требуется откат предыдущей транзакции.")
        elif isinstance(exc, StatementError):
            raise ValueError("Ошибка при подготовке или выполнении SQL-запроса.")
        elif isinstance(exc, DBAPIError):
            raise RuntimeError("Ошибка на уровне DBAPI.")
        elif isinstance(exc, SQLAlchemyError):
            raise RuntimeError("Общая ошибка SQLAlchemy.")
        else:
            raise exc
