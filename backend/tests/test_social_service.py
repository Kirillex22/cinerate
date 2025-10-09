import uuid

import pytest
from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import delete
from sqlmodel import text, SQLModel

from src.domain.entities.user import User, UserPublic, RoleEnum, StatusEnum
from src.services.social.service import SocialService
from src.web.models.users import AccessModel, UserSearchingFilters
from src.infrastructure.repositories.impl.postgres.social_repository.social_repository import PostgresSocialRepository
from src.infrastructure.repositories.impl.postgres.social_repository.orm import UserORM, UserItemORM, SubscribersORM, ActionsORM, UsersActionsHistoryORM
from src.services.social.exceptions import UserNotFoundException, UserDoesntHavePermissionException
from tests.test_film_service import get_session


@pytest.fixture
def sample_user_1():
    return User(userid=str(uuid4()), role=RoleEnum.USER, status=StatusEnum.PRIVATE)


@pytest.fixture
def sample_user_2():
    return User(userid=str(uuid4()), role=RoleEnum.USER, status=StatusEnum.PUBLIC)


@pytest.fixture
def sample_user_3():
    return User(userid=str(uuid4()), role=RoleEnum.ADMIN, status=StatusEnum.PUBLIC)


@pytest.fixture
def access_model(sample_user_1):
    return AccessModel(current_user=sample_user_1)


@pytest.fixture
def filters_for_user(sample_user_1):
    return UserSearchingFilters(target_user=sample_user_1)


@pytest.fixture
def social_service(get_session):
    repo = PostgresSocialRepository(session=get_session)
    return SocialService(repo)


@pytest.fixture(autouse=True)
def clean_db(get_session):
    for table in reversed(list(SQLModel.metadata.sorted_tables)):
        get_session.exec(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
    get_session.commit()


@pytest.fixture
def insert_sample_data(get_session, sample_user_1, sample_user_2, sample_user_3):
    user_item_id1 = uuid4()
    user_item_orm1 = UserItemORM(
        item_id=user_item_id1,
        username="user1_username",
        bio="Loves movies",
        location="New York",
        birth_date=date(1990, 1, 1),
        email="user1@example.com",
        avatar=None,
        subscribers_count=0,
        reviews_count=0,
        playlists_count=0,
        subscribes_count=0,
        role="USER",
        status="PRIVATE"
    )
    get_session.add(user_item_orm1)

    # Вставка UserItem для sample_user_2
    user_item_id2 = uuid4()
    user_item_orm2 = UserItemORM(
        item_id=user_item_id2,
        username="user2_username",
        bio="Film enthusiast",
        location="London",
        birth_date=date(1985, 2, 2),
        email="user2@example.com",
        avatar=None,
        subscribers_count=0,
        reviews_count=0,
        playlists_count=0,
        subscribes_count=0,
        role="USER",
        status="PUBLIC"
    )
    get_session.add(user_item_orm2)

    # Вставка UserItem для sample_user_3
    user_item_id3 = uuid4()
    user_item_orm3 = UserItemORM(
        item_id=user_item_id3,
        username="user3_username",
        bio="Admin user",
        location="Berlin",
        birth_date=date(1980, 3, 3),
        email="user3@example.com",
        avatar=None,
        subscribers_count=0,
        reviews_count=0,
        playlists_count=0,
        subscribes_count=0,
        role="ADMIN",
        status="PUBLIC"
    )
    get_session.add(user_item_orm3)
    get_session.commit()

    # Вставка UserORM с совпадением userid
    user_orm1 = UserORM(
        id=uuid.UUID(sample_user_1.userid),
        full_name="User One",
        login="user1_login",
        hashed_password="hash1",
        item_id=user_item_id1
    )
    user_orm2 = UserORM(
        id=uuid.UUID(sample_user_2.userid),
        full_name="User Two",
        login="user2_login",
        hashed_password="hash2",
        item_id=user_item_id2
    )
    user_orm3 = UserORM(
        id=uuid.UUID(sample_user_3.userid),
        full_name="User Three",
        login="user3_login",
        hashed_password="hash3",
        item_id=user_item_id3
    )
    get_session.add_all([user_orm1, user_orm2, user_orm3])
    get_session.commit()

    # Вставка подписки: user2 подписан на user1
    subscriber = SubscribersORM(
        subscriber_id=user_orm2.id,
        subscribed_id=user_orm1.id
    )
    subscriber2 = SubscribersORM(
        subscriber_id=user_orm1.id,
        subscribed_id=user_orm2.id
    )
    get_session.add(subscriber)
    get_session.add(subscriber2)

    # Вставка действия и истории
    action = ActionsORM(action_id=uuid4(), name="test_action")
    get_session.add(action)
    get_session.commit()

    # Создаём историю действий для user_orm1
    history = UsersActionsHistoryORM(
        user_id=user_orm1.id,
        action_id=action.action_id,
        date=datetime.now(),
        action_attributes={"key": "value"}
    )
    get_session.add(history)
    get_session.commit()

    return user_orm1.id, user_orm2.id, user_orm3.id


# get_user() TESTS
def test_get_user_success(social_service, sample_user_1, access_model, insert_sample_data):
    filters = UserSearchingFilters(target_user=access_model.current_user)
    result = social_service.get_user(access_model, filters)
    assert isinstance(result, UserPublic)
    assert result.userid == sample_user_1.userid
    assert result.username == "user1_username"


def test_get_user_no_permission(social_service, sample_user_1, sample_user_2):
    access_model = AccessModel(current_user=sample_user_2)
    filters = UserSearchingFilters(target_user=sample_user_1)
    with pytest.raises(UserDoesntHavePermissionException):
        social_service.get_user(access_model, filters)


def test_get_user_not_found(social_service, sample_user_1):
    non_existent_user = User(userid=str(uuid4()), role=RoleEnum.USER, status=StatusEnum.PUBLIC)  # Изменён на PUBLIC
    access_model = AccessModel(current_user=sample_user_1)
    filters = UserSearchingFilters(target_user=non_existent_user)
    with pytest.raises(UserNotFoundException):
        social_service.get_user(access_model, filters)


# search_users() TESTS
def test_search_users_success(social_service, access_model, insert_sample_data):
    access_model.current_user.role = RoleEnum.ADMIN
    access_model.current_user.status = StatusEnum.PUBLIC
    filters = UserSearchingFilters(username="user1_username", userid=access_model.current_user.userid)
    results = social_service.search_users(access_model, filters)
    assert len(results) == 1
    assert results[0].userid == access_model.current_user.userid


def test_search_users_no_results(social_service, access_model):
    filters = UserSearchingFilters(username="nonexistent")
    with pytest.raises(UserNotFoundException):
        social_service.search_users(access_model, filters)


# # get_subscribers() TESTS
def test_get_subscribers_success(social_service, sample_user_1, access_model, insert_sample_data):
    filters = UserSearchingFilters(target_user=access_model.current_user)
    results = social_service.get_subscribers(access_model, filters)
    assert len(results) == 1
    assert results[0].username == "user2_username"


def test_get_subscribers_no_permission(social_service, sample_user_2, sample_user_1):
    access_model = AccessModel(current_user=sample_user_2)
    filters = UserSearchingFilters(target_user=sample_user_1)
    with pytest.raises(UserDoesntHavePermissionException):
        social_service.get_subscribers(access_model, filters)


# get_subscribes() TESTS
def test_get_subscribes_success(social_service, access_model, insert_sample_data):
    user_orm1_id, user_orm2_id, _ = insert_sample_data
    access_model.current_user.userid = str(user_orm2_id)
    access_model.current_user.status = StatusEnum.PUBLIC
    filters = UserSearchingFilters(target_user=access_model.current_user)
    results = social_service.get_subscribes(access_model, filters)
    assert len(results) == 1
    assert results[0].username == "user1_username"


def test_get_subscribes_no_subscriptions(social_service, access_model):
    filters = UserSearchingFilters(target_user=access_model.current_user)
    with pytest.raises(UserNotFoundException):
        social_service.get_subscribes(access_model, filters)


# get_actions_history() TESTS
def test_get_actions_history_success(get_session, sample_user_1, sample_user_2, insert_sample_data):
    repo = PostgresSocialRepository(session=get_session)
    social_service = SocialService(repo)

    access_model = AccessModel(current_user=sample_user_2)
    filters = UserSearchingFilters(target_user=sample_user_2)

    action = ActionsORM(action_id=uuid.uuid4(), name="test_action")
    get_session.add(action)
    get_session.commit()

    history = UsersActionsHistoryORM(
        user_id=uuid.UUID(sample_user_1.userid),
        action_id=action.action_id,
        date=datetime.now(),
        action_attributes={"key": "value"}
    )
    get_session.add(history)
    get_session.commit()
    get_session.refresh(history)
    print("Refreshed history:", history)

    date_start = datetime(2000, 1, 1)
    results = social_service.get_actions_history(access_model, filters, date_start)

    assert len(results) == 2
    assert results[0].name == "test_action"
    assert results[0].action_attributes == {"key": "value"}


def test_get_actions_history_no_permission(social_service, sample_user_2, sample_user_1):
    access_model = AccessModel(current_user=sample_user_2)
    filters = UserSearchingFilters(target_user=sample_user_1)
    date_start = datetime(2000, 1, 1)
    with pytest.raises(UserDoesntHavePermissionException):
        social_service.get_actions_history(access_model, filters, date_start)


# subscribe() TESTS
def test_subscribe_success(social_service, sample_user_1, sample_user_2, insert_sample_data):
    filters = UserSearchingFilters(target_user=sample_user_2)
    social_service.subscribe(sample_user_1, filters)
    access_model = AccessModel(current_user=sample_user_2)
    filters = UserSearchingFilters(target_user=sample_user_2)
    subscribers = social_service.get_subscribers(access_model, filters)
    assert len(subscribers) == 1
    assert any(subscriber.userid == sample_user_1.userid for subscriber in subscribers)


def test_subscribe_no_permission(social_service, sample_user_1, sample_user_2, insert_sample_data):
    sample_user_2.status = StatusEnum.PRIVATE
    filters = UserSearchingFilters(target_user=sample_user_2)
    with pytest.raises(UserDoesntHavePermissionException) as exc_info:
        social_service.subscribe(sample_user_1, filters)
    assert exc_info.value.code == "NOT ENOUGH RIGHTS"
    assert str(sample_user_1.userid) in str(exc_info.value)
    assert str(sample_user_2.userid) in str(exc_info.value)


# unsubscribe() TESTS
def test_unsubscribe_success(social_service, sample_user_1, sample_user_2, insert_sample_data, get_session):
    get_session.exec(delete(SubscribersORM))
    get_session.commit()

    filters = UserSearchingFilters(target_user=sample_user_2)
    social_service.subscribe(sample_user_1, filters)
    social_service.unsubscribe(sample_user_1, filters)
    access_model = AccessModel(current_user=sample_user_2)
    filters = UserSearchingFilters(target_user=sample_user_2)

    with pytest.raises(UserNotFoundException):
        social_service.get_subscribers(access_model, filters)


def test_update_profile_success(social_service, access_model, insert_sample_data):
    updated_profile = UserPublic(userid=access_model.current_user.userid, bio="updated_bio")
    social_service.update_profile(access_model, updated_profile)
    filters = UserSearchingFilters(target_user=access_model.current_user)
    updated_profile_from_db = social_service.get_user(access_model, filters)
    assert updated_profile_from_db.bio == "updated_bio"


def test_update_profile_no_permission(social_service, sample_user_1, sample_user_2):
    access_model = AccessModel(current_user=sample_user_2)
    updated_profile = UserPublic(userid=sample_user_1.userid, bio="updated_bio")
    with pytest.raises(UserDoesntHavePermissionException):
        social_service.update_profile(access_model, updated_profile)

