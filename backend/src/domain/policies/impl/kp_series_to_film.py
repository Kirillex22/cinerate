from src.domain.entities.film import FilmBase
from src.domain.policies.core.base_series_to_film_policy import BaseSeriesToFilmPolicy
from src.domain.exceptions import TransformToSeasonException


class DefaultSeriesToFilmPolicy(BaseSeriesToFilmPolicy):
    def execute(self, series: FilmBase) -> None:
        if series.is_series and series.season:
            series.filmid = f'{series.filmid}-{series.season}'
            series.is_series = False
            return
        raise TransformToSeasonException(series.season)
