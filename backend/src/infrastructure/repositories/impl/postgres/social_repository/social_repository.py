import uuid
from abc import ABC
from datetime import datetime
from typing import Optional, List, Union

from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from functools import wraps

from src.infrastructure.repositories.core.base_social_repository import BaseSocialRepository
from src.domain.entities.user import User, UserPublic, UserPreview, UserHistoryModel, UserInDb, UserRegisterPrepared
from src.shared.mappers.orm_to_model import orm_join_to_user_public, orm_join_to_user_preview, orm_join_to_user_history, \
    user_orm_to_user_in_db

from src.shared.mappers.orms_to_dict import merge_dicts
from src.infrastructure.repositories.impl.postgres.social_repository.orm import UserORM, UserItemORM, SubscribersORM, ActionsORM, \
    UsersActionsHistoryORM
from src.infrastructure.repositories.impl.postgres.social_repository.tools.postgres_local_functions import get_subscribers_count, \
    get_subscribes_count, create_stored_functions
from src.infrastructure.repositories.impl.postgres.social_repository.tools.query_builders import LocalUserSearchQueryBuilder
from src.shared.exceptions.base_exception_handler import BaseExceptionHandler
from src.services.social.exceptions import UserNotFoundException
from src.web.models.users import UserSearchingFilters, AccessModel


def wrap_query(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            func_result = func(self, *args, **kwargs)
            self._session.commit()
            return func_result

        except Exception as e:
            self._session.rollback()
            raise e

    return wrapper


class PostgresSocialRepository(BaseSocialRepository, ABC):
    def __init__(self, session: Session, exception_handler: BaseExceptionHandler = None):
        self._exception_handler = exception_handler
        self._session = session
        create_stored_functions(self._session)

    @wrap_query
    def create_user(self, user_to_register: UserRegisterPrepared, is_admin: Optional[bool] = False) -> None:
        item_orm = UserItemORM(
            email=user_to_register.email,
            birth_date=user_to_register.birth_date,
            status='PRIVATE',
            username=user_to_register.login
        )

        if is_admin:
            item_orm.role = 'ADMIN'
        else:
            item_orm.role = 'USER'

        self._session.add(item_orm)
        self._session.flush()

        user_orm = UserORM(
            login=user_to_register.login,
            hashed_password=user_to_register.hashed_password,
            item_id=item_orm.item_id,
        )
        self._session.add(user_orm)

    def update_fields(self, users):
        for user in users:
            if user.dict().get('subscribers_count'):
                user.subscribers_count = get_subscribers_count(user.userid, self._session)
            if user.dict().get('subscribes_count'):
                user.subscribes_count = get_subscribes_count(user.userid, self._session)

        return users

    def get_user(self, user: Optional[User], login: Optional[str] = None) -> Optional[Union[UserPublic, UserInDb]]:
        if login is not None:
            query = (
                select(UserORM)
                .where(UserORM.login == login)
            )

            db_response = next(self._session.exec(query), None)
            if not db_response:
                return None

            return user_orm_to_user_in_db(db_response)

        uid = user.userid
        query = (
            select(UserORM)
            .options(selectinload(UserORM.user_item))
            .where(UserORM.id == uid)
        )

        db_response = next(self._session.exec(query), None)

        if not db_response:
            return None

        user_public = orm_join_to_user_public(
            merge_dicts(db_response, db_response.user_item)
        )

        return user_public

    def search_users(self, filters: UserSearchingFilters) -> List[UserPreview]:
        query = select(UserORM)
        builder = LocalUserSearchQueryBuilder(query)
        query = builder.apply_all(filters).build()
        db_response = self._session.exec(query).all()

        result = self.update_fields([
            orm_join_to_user_preview(
                merge_dicts(user, user.user_item if user.user_item else UserItemORM())
            )
            for user in db_response
        ])

        if len(result) > 0:
            return result

        return []

    def get_subscribers(self, user: User) -> List[UserPreview]:
        uid = user.userid
        subquery = (
            select(SubscribersORM.subscribed_id)
            .where(SubscribersORM.subscriber_id == uid)
        )
        query = (
            select(UserORM)
            .where(UserORM.id.in_(subquery))
            .options(selectinload(UserORM.user_item))
        )
        db_response = self._session.exec(query).all()

        result = self.update_fields([
            orm_join_to_user_preview(
                merge_dicts(user,
                            user.user_item if user.user_item else UserItemORM())
            )
            for user in db_response
        ])

        if len(result) > 0:
            return result

        return []

    def get_subscribes(self, user: User) -> List[UserPreview]:
        uid = user.userid
        subquery = (
            select(SubscribersORM.subscriber_id)
            .where(SubscribersORM.subscribed_id == uid)
        )
        query = (
            select(UserORM)
            .where(UserORM.id.in_(subquery))
            .options(selectinload(UserORM.user_item))
        )
        db_response = self._session.exec(query).all()

        result = self.update_fields([
            orm_join_to_user_preview(
                merge_dicts(user,
                            user.user_item if user.user_item else UserItemORM())
            )
            for user in db_response
        ])

        if len(result) > 0:
            return result

        return []

    def get_actions_history(self, user: User, date_start: datetime) -> List[UserHistoryModel]:
        uid = user.userid
        subscribed_ids_subquery = (
            select(SubscribersORM.subscribed_id)
            .where(SubscribersORM.subscriber_id == uid)
        )

        user_ids_subquery = (
            select(UserORM.id)
            .where(UserORM.id.in_(subscribed_ids_subquery))
        )

        query = (
            select(UsersActionsHistoryORM)
            .where(UsersActionsHistoryORM.user_id.in_(user_ids_subquery))
            .where(UsersActionsHistoryORM.date >= date_start)
            .options(selectinload(UsersActionsHistoryORM.action))
        )
        db_response = self._session.exec(query).all()

        result = [
            orm_join_to_user_history(
                merge_dicts(user_history,
                            user_history.action if user_history.action else ActionsORM())
            )
            for user_history in db_response
        ]

        if len(result) > 0:
            return result

        return []

    @wrap_query
    def subscribe(self, current_user: User, user_to_sub: User) -> None:
        new_subscription = SubscribersORM(
            subscriber_id=uuid.UUID(user_to_sub.userid),
            subscribed_id=uuid.UUID(current_user.userid),
        )

        self._session.add(new_subscription)

    @wrap_query
    def unsubscribe(self, current_user: User, user_to_unsub: User) -> None:
        subscriber_id = uuid.UUID(user_to_unsub.userid)
        subscribed_id = uuid.UUID(current_user.userid)

        query = (
            delete(SubscribersORM)
            .where(
                SubscribersORM.subscriber_id == subscriber_id,
                SubscribersORM.subscribed_id == subscribed_id,
            )
        )
        self._session.exec(query)

    @wrap_query
    def update_profile(self, user: UserPublic) -> None:
        user_id = uuid.UUID(user.userid)

        query = (
            select(UserORM)
            .where(UserORM.id == user_id)
        )
        db_response = self._session.exec(query).first()
        if not db_response:
            raise UserNotFoundException(
                AccessModel(
                    current_user=user
                ), filters=UserSearchingFilters(target_user=None))

        user_item: UserItemORM = db_response.user_item

        custom_attributes = user.get_custom_non_null_fields()
        if custom_attributes.get('role'):
            custom_attributes['role'] = custom_attributes['role'].name
        if custom_attributes.get('status'):
            custom_attributes['status'] = custom_attributes['status'].name

        user_item.update_user_item_orm_from_model(custom_attributes)
