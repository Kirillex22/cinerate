from datetime import date, datetime
from typing import Optional

from dateutil.parser import parse
from pydantic import BaseModel, Field, field_validator
from enum import IntEnum


class RoleEnum(IntEnum):
    ADMIN = 1
    USER = 2


class StatusEnum(IntEnum):
    PRIVATE = 1
    PUBLIC = 2


class UserBase(BaseModel):
    userid: str = Field(..., description='Идентификатор пользователя')


class User(UserBase):
    role: Optional[RoleEnum] = Field(default=RoleEnum.USER,
                                     description="Роль пользователя (админ/обычный пользователь)")
    status: Optional[StatusEnum] = Field(default=StatusEnum.PRIVATE, description='Статус профиля (публичный/приватный)')


class UserPublic(User):
    username: Optional[str] = Field(default="Пользователь", description='Отображаемое имя пользователя')
    bio: Optional[str] = Field(default=None, description='Выставляемый статус в профиле')
    location: Optional[str] = Field(default=None, description='Условный адрес пользователя (напр. "Omsk, Russia")')
    birth_date: Optional[date] = Field(default=None, description='Дата рождения')
    email: Optional[str] = Field(default=None, description='email пользователя')
    avatar: Optional[str] = Field(default=None, description='Картинка профиля')

    @field_validator('birth_date', mode='before')
    def validate_birth_date(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, date):
            return v
        # Попытка распарсить строку в дату
        try:
            parsed_date = parse(v).date()
            return parsed_date
        except Exception:
            # Если парсинг не удался, возвращаем None
            return None


    def get_custom_non_null_fields(self) -> dict:
        exclude_fields = {"userid", "role"}
        return {
            k: v for k, v in self.dict(exclude_unset=True).items()
            if k not in exclude_fields and v is not None
        }


class UserInDb(UserBase):
    login: str
    hashed_password: str
    role: Optional[RoleEnum] = None


class UserRegisterForm(BaseModel):
    login: str
    password: str
    email: Optional[str] = None
    birth_date: Optional[date] = None


class UserRegisterPrepared(BaseModel):
    login: str
    hashed_password: str
    email: Optional[str] = None
    birth_date: Optional[date] = None


class UserPreview(User):
    username: str = Field(default="Пользователь", description='Отображаемое имя пользователя')
    subscribers_count: int = Field(default=0, ge=0, description='Количество подписчиков')
    avatar: Optional[str] = Field(default=None, description='Картинка профиля')


class UserExtended(UserPreview):
    reviews_count: int = Field(default=0, ge=0, description='Количество рецензий (оценок) на фильмы')
    playlists_count: int = Field(default=0, ge=0, description='Количество плейлистов пользователя')
    subscribes_count: int = Field(default=0, ge=0, description='Количество подписок пользователя')


class UserHistoryModel(BaseModel):
    aid: str = Field(..., description='Идентификатор события')
    uid: str = Field(..., description='Идентификатор пользователя, которому принадлежит событие')
    name: str = Field(..., description='Описания события')
    date: datetime = Field(default=datetime.now(), description='Дата, когда событие произошло')
    action_attributes: dict = Field(..., description='Параметры события (названия фильмов, плейлистов)')
