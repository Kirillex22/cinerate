from collections.abc import Generator

from sqlmodel import SQLModel, create_engine, Session

from src.config.settings import AppSettings


class Database:
    def __init__(self, settings: AppSettings, echo: bool = False):
        self.settings = settings

        db_url = settings.POSTGRES_SETTINGS.make_url()
        self.engine = create_engine(db_url, echo=echo)

    def init_db(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session]:
        with Session(self.engine) as session:
            yield session
