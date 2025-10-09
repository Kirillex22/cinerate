from typing import Optional
from pydantic import BaseModel, Field

from src.domain.entities.user import User, RoleEnum, StatusEnum


def is_public(target_user: User) -> bool:
    return target_user.status == StatusEnum.PUBLIC


class AccessModel(BaseModel):
    current_user: User

    def is_owner(self, target_user: User) -> bool:
        return self.current_user.userid == target_user.userid

    def is_admin(self) -> bool:
        return self.current_user.role == RoleEnum.ADMIN


class UserSearchingFilters(BaseModel):
    target_user: Optional[User] = Field(default=None,
                                        description='Пользователь к которому применяются какие-либо методы')
    userid: Optional[str] = Field(default=None, description='Идентификатор пользователя')
    username: Optional[str] = Field(default=None, description='Отображаемое имя пользователя')
    root: Optional[bool] = Field(default=False, description='Права доступа (на поиск приватных аккаунтов)')
    login: Optional[str] = Field(default=None, description='Логин пользователя')

    def get_non_null_fields(self) -> dict:
        return {k: v for k, v in self.dict().items() if v is not None}
