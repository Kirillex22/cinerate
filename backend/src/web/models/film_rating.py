from enum import IntEnum
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field

T = TypeVar('T', bound=IntEnum)


class BaseRatingScale(IntEnum):
    BAD = 1
    NORMAL = 2
    GOOD = 3
    AWESOME = 4


class BaseFilmComplexRating(BaseModel, Generic[T]):
    storyline: Optional[T] = Field(None, description='Сюжетная линия')
    music: Optional[T] = Field(None, description='Музыкальное сопровождение')
    montage: Optional[T] = Field(None, description='Качество монтажа и операторской работы')
    acting_game: Optional[T] = Field(None, description='Игра актеров')
    atmosphere: Optional[T] = Field(None, description='Атмосферность')
    originality: Optional[T] = Field(None, description='Оригинальность идеи')

    def __iter__(self):
        return iter(self.__dict__.items())
