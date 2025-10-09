from abc import abstractmethod
from typing import List, Optional, Union
from datetime import datetime

from src.domain.entities.user import User, UserPublic, UserPreview, UserHistoryModel, UserInDb, \
    UserRegisterPrepared
from src.web.models.users import UserSearchingFilters


class BaseSocialRepository:
    @abstractmethod
    def create_user(self, user_to_register: UserRegisterPrepared, is_admin: bool = False) -> None:
        pass

    @abstractmethod
    def get_user(self, user: Optional[User], login: Optional[str] = None) -> Optional[Union[UserPublic, UserInDb]]:
        pass

    @abstractmethod
    def search_users(self, filters: UserSearchingFilters) -> List[UserPreview]:
        pass

    @abstractmethod
    def get_subscribers(self, user: User) -> List[UserPreview]:
        pass

    @abstractmethod
    def get_subscribes(self, user: User) -> List[UserPreview]:
        pass

    @abstractmethod
    def get_actions_history(self, user: User, date_start: datetime) -> List[UserHistoryModel]:
        pass

    @abstractmethod
    def subscribe(self, current_user: User, user_to_sub: User) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, current_user: User, user_to_unsub: User) -> None:
        pass

    @abstractmethod
    def update_profile(self, user: UserPublic) -> None:
        pass
