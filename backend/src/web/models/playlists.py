from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from src.domain.entities.playlist import Playlist, PlaylistItem
from src.domain.entities.user import User
from src.web.models.search_filters import SearchingFiltersWithUserData


# Входная модель для создания плейлиста.
class CreatePlaylistModel(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool
    gen_attrs: Optional[SearchingFiltersWithUserData] = None


# Входная модель фильтров поиска плейлистов.
class PlaylistSearchFilters(BaseModel):
    playlistid: Optional[str] = Field(None,
                                      description='Идентификатор плейлиста. ')
    target_user: Optional[User] = Field(None,
                                        description='Целевой пользователь. ')

    name: Optional[str] = Field(None,
                                description='Название плейлиста.')
    only_public: Optional[bool] = Field(None,
                                        description='Указывать бесполезно. Контролируется изнутри.')

    def left_only_playlistid(self) -> "PlaylistSearchFilters":
        return PlaylistSearchFilters(playlistid=self.playlistid)


class PrivatePlaylistSearchFilters(PlaylistSearchFilters):
    pass


FiltersFields = Enum(
    'FiltersFields',
    {field.upper(): field for field in PlaylistSearchFilters.model_fields.keys()},
    type=str
)


class AccessModel(BaseModel):
    current_user: User

    def is_owner(self, playlist: Playlist) -> bool:
        return self.current_user.userid == playlist.userid

    def is_collaborator(self, playlist: Playlist) -> bool:
        return self.current_user.userid in playlist.collaborators

    def is_creator(self, playlist_item: PlaylistItem) -> bool:
        return self.current_user.userid == playlist_item.creatorid
