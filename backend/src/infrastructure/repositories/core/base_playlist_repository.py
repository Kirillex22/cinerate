from abc import abstractmethod
from typing import List, Optional, Union

from src.domain.entities.film import FilmBase
from src.domain.entities.playlist import Playlist, PlaylistItem, PlaylistItemPreview
from src.domain.entities.user import User
from src.web.models.playlists import CreatePlaylistModel, PlaylistSearchFilters


class BasePlaylistRepository:
    @abstractmethod
    def create_playlist(self, user: User, create_model: CreatePlaylistModel) -> str:
        pass

    @abstractmethod
    def autofill_playlist(self, filters: PlaylistSearchFilters) -> None:
        pass

    @abstractmethod
    def get_playlists(self, filters: PlaylistSearchFilters) -> Optional[Union[List[Playlist], Playlist]]:
        pass

    @abstractmethod
    def remove_playlist(self, filters: PlaylistSearchFilters) -> None:
        pass

    @abstractmethod
    def add_to_playlist(self, filters: PlaylistSearchFilters, film_to_add: FilmBase, contributor: User) -> None:
        pass

    @abstractmethod
    def get_playlist_item(self, filters: PlaylistSearchFilters, film_to_get: FilmBase) -> Optional[PlaylistItem]:
        pass

    @abstractmethod
    def remove_playlist_item(self, filters: PlaylistSearchFilters, film_to_remove: FilmBase) -> None:
        pass

    @abstractmethod
    def update_playlist(self, playlist: Playlist) -> None:
        pass

    @abstractmethod
    def get_playlist_content(self, filters: PlaylistSearchFilters) -> Optional[List[PlaylistItemPreview]]:
        pass

    @abstractmethod
    def get_playlist_by_id(self, playlistid: str) -> Optional[Playlist]:
        pass
