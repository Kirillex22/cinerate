from abc import abstractmethod

from src.domain.entities.film import FilmBase


class BaseSeriesToFilmPolicy:
    @abstractmethod
    def execute(self, series: FilmBase) -> None:
        pass
