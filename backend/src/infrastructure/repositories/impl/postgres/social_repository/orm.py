from typing import Optional, List, Dict, Any
from sqlalchemy import CheckConstraint, Column, JSON, ForeignKey
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserItemORM(SQLModel, table=True):
    __tablename__ = "user_item"

    item_id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))

    username: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=255)
    birth_date: Optional[date] = Field(default=None)
    email: Optional[str] = Field(default=None, max_length=255)
    avatar: Optional[str] = Field(default=None, max_length=2048)
    subscribers_count: int = Field(default=0)
    reviews_count: int = Field(default=0)
    playlists_count: int = Field(default=0)
    subscribes_count: int = Field(default=0)
    role: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=50)

    user: Optional["UserORM"] = Relationship(back_populates="user_item")

    __table_args__ = (
        CheckConstraint("subscribers_count >= 0", name="chk_subscribers_count_nonnegative"),
        CheckConstraint("reviews_count >= 0", name="chk_reviews_count_nonnegative"),
        CheckConstraint("playlists_count >= 0", name="chk_playlists_count_nonnegative"),
        CheckConstraint("subscribes_count >= 0", name="chk_subscribes_count_nonnegative"),
        CheckConstraint("role IN ('ADMIN', 'USER')", name="chk_role_enum"),
        CheckConstraint("status IN ('PRIVATE', 'PUBLIC')", name="chk_status_enum"),
    )

    def update_user_item_orm_from_model(self, user_item_custom_data: dict):
        for key, value in user_item_custom_data.items():
            setattr(self, key, value)


class UserORM(SQLModel, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    full_name: Optional[str] = Field(default=None, max_length=255)
    login: str = Field(max_length=255, unique=True)
    hashed_password: str = Field(max_length=255)

    item_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("user_item.item_id", ondelete="CASCADE"), nullable=False,
                         index=True),
    )

    user_item: Optional[UserItemORM] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "single_parent": True,
            "uselist": False,
        },
    )
    subscriptions: List["SubscribersORM"] = Relationship(
        back_populates="subscriber_user",
        sa_relationship_kwargs={"foreign_keys": "[SubscribersORM.subscriber_id]"},
    )
    subscribers: List["SubscribersORM"] = Relationship(
        back_populates="subscribed_user",
        sa_relationship_kwargs={"foreign_keys": "[SubscribersORM.subscribed_id]"},
    )
    actions_history: List["UsersActionsHistoryORM"] = Relationship(back_populates="user")


class SubscribersORM(SQLModel, table=True):
    __tablename__ = "subscribers"

    sub_id: Optional[int] = Field(default=None, primary_key=True)
    subscribed_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True),
    )
    subscriber_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True),
    )

    subscribed_user: Optional[UserORM] = Relationship(
        back_populates="subscribers",
        sa_relationship_kwargs={"foreign_keys": "[SubscribersORM.subscribed_id]"},
    )

    subscriber_user: Optional[UserORM] = Relationship(
        back_populates="subscriptions",
        sa_relationship_kwargs={"foreign_keys": "[SubscribersORM.subscriber_id]"},
    )


class ActionsORM(SQLModel, table=True):
    __tablename__ = "actions"

    action_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, unique=True, index=True, nullable=False),
    )
    name: str = Field(max_length=255)

    users_actions_history: List["UsersActionsHistoryORM"] = Relationship(back_populates="action")


class UsersActionsHistoryORM(SQLModel, table=True):
    __tablename__ = "users_actions_history"

    uah_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True),
    )
    action_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("actions.action_id"), nullable=False, index=True),
    )
    date: datetime = Field()
    action_attributes: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    user: Optional[UserORM] = Relationship(back_populates="actions_history")
    action: Optional[ActionsORM] = Relationship(back_populates="users_actions_history")
