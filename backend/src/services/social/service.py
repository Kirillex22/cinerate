from datetime import datetime
from typing import List

from src.infrastructure.repositories.core.base_social_repository import BaseSocialRepository
from src.domain.entities.user import UserPublic, UserPreview, UserHistoryModel, StatusEnum, User
from src.services.social.exceptions import *
from src.web.models.users import AccessModel, UserSearchingFilters


class SocialService:
    def __init__(self, repository: BaseSocialRepository):
        self._repository = repository

    def get_user(self, access_model: AccessModel, filters: UserSearchingFilters) -> UserPublic:
        user = self._repository.get_user(filters.target_user)
        if not user:
            raise UserNotFoundException(access_model, filters)

        if (access_model.is_owner(filters.target_user)
                or access_model.is_admin() or user.status == StatusEnum.PUBLIC
        ):
            return user

        raise UserDoesntHavePermissionException(access_model, filters, 'get profile')

    def search_users(self, access_model: AccessModel, filters: UserSearchingFilters) -> List[UserPreview]:
        if access_model.is_admin():
            filters.root = True
            users = self._repository.search_users(filters)
        else:
            users = self._repository.search_users(filters)

        if len(users) == 0:
            # ????
            raise UserNotFoundException(access_model, filters)

        return users

    def get_subscribers(self, access_model: AccessModel, filters: UserSearchingFilters) -> List[UserPreview]:
        user = self._repository.get_user(filters.target_user)
        if not user:
            raise UserNotFoundException(access_model, filters)

        if (access_model.is_owner(filters.target_user)
                or access_model.is_admin()
                or user.status == StatusEnum.PUBLIC):
            subscribers = self._repository.get_subscribers(filters.target_user)

            if len(subscribers) == 0:
                raise UserNotFoundException(access_model, filters)

            return subscribers

        raise UserDoesntHavePermissionException(access_model, filters, 'get subscribers')

    def get_subscribes(self, access_model: AccessModel, filters: UserSearchingFilters) -> List[UserPreview]:
        user = self._repository.get_user(filters.target_user)
        if not user:
            raise UserNotFoundException(access_model, filters)

        if (access_model.is_owner(filters.target_user)
                or access_model.is_admin()
                or user.status == StatusEnum.PUBLIC):
            subscribes = self._repository.get_subscribes(filters.target_user)

            if len(subscribes) == 0:
                raise UserNotFoundException(access_model, filters)

            return subscribes

        raise UserDoesntHavePermissionException(access_model, filters, 'get subscribes')

    def get_actions_history(self, access_model: AccessModel, filters: UserSearchingFilters, date_start: datetime) \
            -> List[UserHistoryModel]:
        if access_model.is_owner(filters.target_user) or access_model.is_admin():
            actions_history = self._repository.get_actions_history(filters.target_user, date_start)

            if len(actions_history) == 0:
                raise UserNotFoundException(access_model, filters)

            return actions_history

        raise UserDoesntHavePermissionException(access_model, filters, 'get actions history')

    def subscribe(self, current_user: User, filters: UserSearchingFilters) -> None:
        user = self._repository.get_user(filters.target_user)
        if not user:
            raise UserNotFoundException(AccessModel(current_user=current_user), filters)

        if (current_user.userid != filters.target_user.userid) and (user.status == StatusEnum.PUBLIC):
            self._repository.subscribe(current_user, filters.target_user)
            return

        raise UserDoesntHavePermissionException(AccessModel(current_user=current_user), filters, 'subscribe')

    def unsubscribe(self, current_user: User, filters: UserSearchingFilters) -> None:
        if current_user.userid != filters.target_user.userid:
            self._repository.unsubscribe(current_user, filters.target_user)
            return

        raise UserDoesntHavePermissionException(AccessModel(current_user=current_user), filters, 'unsubscribe')

    def update_profile(self, access_model: AccessModel, target_user: UserPublic) -> None:
        if access_model.is_owner(target_user) or access_model.is_admin():
            self._repository.update_profile(target_user)
            return

        raise UserDoesntHavePermissionException(access_model, UserSearchingFilters(target_user=target_user),
                                                'update_profile')
