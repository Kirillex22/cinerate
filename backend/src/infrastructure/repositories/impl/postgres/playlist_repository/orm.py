import uuid
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKeyConstraint, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from src.infrastructure.repositories.impl.postgres.film_repository.orm import Film


class PlaylistORM(SQLModel, table=True):
    __tablename__ = "playlists"

    playlistid: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    userid: uuid.UUID = Field(index=True, foreign_key="user.id")  # просто поле, не часть PK
    name: str = Field(nullable=False)
    description: Optional[str] = Field()
    is_public: Optional[bool] = Field(default=False)
    additions_count: int = Field(default=0)

    gen_attrs: Optional[Dict[str, object]] = Field(default=None, sa_column=Column(JSONB))
    collaborators: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))

    items: List["PlaylistItemORM"] = Relationship(
        back_populates="playlist",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete"}
    )

    def update_playlist_orm_from_model(self, playlist_custom_data: dict):
        for key, value in playlist_custom_data.items():
            setattr(self, key, value)


class PlaylistItemORM(SQLModel, table=True):
    __tablename__ = "playlist_items"

    playlistid: uuid.UUID = Field(sa_column=Column(UUID(as_uuid=True)))
    filmid: str = Field(nullable=False)
    creatorid: Optional[str] = Field(default=None)

    film: Optional[Film] = Relationship(
        back_populates=None,
        sa_relationship_kwargs={"lazy": "selectin", "passive_deletes": True}
    )

    playlist: Optional[PlaylistORM] = Relationship(
        back_populates="items",
        sa_relationship_kwargs={"lazy": "selectin", "passive_deletes": True}
    )

    __table_args__ = (
        PrimaryKeyConstraint("playlistid", "filmid", name="pk_playlist_item"),
        ForeignKeyConstraint(
            ["playlistid"],
            ["playlists.playlistid"],
            ondelete="CASCADE"
        ),
        ForeignKeyConstraint(
            ["filmid"],
            ["films.filmid"],
            ondelete="CASCADE"
        ),
    )
