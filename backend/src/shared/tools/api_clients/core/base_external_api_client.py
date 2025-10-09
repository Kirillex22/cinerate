from abc import abstractmethod
from typing import List

from src.domain.entities.film import FilmPreview, FilmExtended
from src.web.models.search_filters import BaseApiSearchingFilters


# Попробовал переделать кал
class BaseExternalAPIClient:
    @abstractmethod
    def get(self, filters: BaseApiSearchingFilters) -> FilmExtended:
        pass

    @abstractmethod
    def search_by_filters(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        pass

    @abstractmethod
    def search_by_name(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        pass

    @abstractmethod
    def search_seasons(self, filters: BaseApiSearchingFilters) -> List[FilmPreview]:
        pass

    @abstractmethod
    def get_all_seasons(self, filters: BaseApiSearchingFilters) -> List[FilmExtended]:
        pass
