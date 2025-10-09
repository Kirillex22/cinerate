from typing import Optional, List
from pydantic import BaseModel, Field

from src.domain.entities.film import FilmPreview, FilmExtended
from src.web.models.search_filters import SearchingFiltersWithUserData


class Playlist(BaseModel):
    userid: str = Field(..., description='Идентификатор пользователя, которому принадлежит плейлист')
    playlistid: str = Field(..., description='Идентификатор плейлиста относительно владельца')
    name: str = Field(..., description='Название плейлиста')
    description: str = Field(None, description='Описание плейлиста')
    is_public: Optional[bool] = Field(default=False, description='Доступность плейлиста (коллабораторам без разницы)')
    additions_count: int = Field(default=False, description='Количество добавлений в избранное')
    gen_attrs: Optional[SearchingFiltersWithUserData] = Field(None,
                                                              description='Атрибуты для автоматического формирования плейлиста')
    collaborators: Optional[List[str]] = Field(default=[],
                                               description='''
                                               Список userid пользователей, имеющих возможность редактировать и просматривать плейлист вне зависимости от публичности
                                               ''')

    def get_custom_non_null_fields(self) -> dict:
        exclude_fields = {"userid", "playlistid"}
        return {
            k: v for k, v in self.dict().items()
            if k not in exclude_fields and v is not None
        }


class PlaylistItem(BaseModel):
    playlistid: str = Field(..., description='Идентификатор плейлиста относительно владельца')
    filmid: str = Field(..., description='Идентификатор фильма')
    creatorid: Optional[str] = Field(default=None,
                                     description='Идентификатор пользователя, который создал данную позицию в плейлисте; если None - создатель это владелец плейлиста')


class PlaylistItemPreview(BaseModel):
    item: PlaylistItem = Field(..., description='Модель для описания фильма как элемента плейлиста')
    preview: FilmPreview = Field(..., description='Модель для описания фильма как структуры данных')


class PlaylistItemExtended(BaseModel):
    item: PlaylistItem = Field(..., description='Модель для описания фильма как элемента плейлиста')
    extended: FilmExtended = Field(..., description='Модель для описания фильма как структуры данных')
