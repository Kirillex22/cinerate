import uuid
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale


class Film(SQLModel, table=True):
    __tablename__ = "films"

    filmid: str = Field(primary_key=True)
    poster_link: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    release_year: Optional[int] = Field(default=None)
    is_series: bool
    season: Optional[int] = Field(default=None)
    alternative_name: Optional[str] = None
    genres: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    slogan: Optional[str] = None
    countries: List[str] = Field(default_factory=list, sa_column=Column(JSONB))
    director: Optional[str] = None
    description: str
    time_minutes: Optional[int] = None
    ratings: Optional[Dict[str, Optional[float]]] = Field(default=None, sa_column=Column(JSONB))
    trailers: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    end_year: Optional[int] = None
    status: Optional[str] = None
    tops: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    last_updated: Optional[datetime] = None
    persons: Optional[List[Dict]] = Field(default=None, sa_column=Column(JSONB))
    episodes: Optional[List[Dict]] = Field(default=None, sa_column=Column(JSONB))
    age_rating: Optional[int] = None


class UserFilm(SQLModel, table=True):
    __tablename__ = "user_films"

    filmid: str = Field()
    userid: uuid.UUID = Field(
        foreign_key="user.id",  # <-- ссылка на UserORM.id
        index=True,
    )
    is_watched: bool = False
    added_at: Optional[datetime] = Field(default=None)
    user_rating: Optional[Dict[str, int]] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    def set_watch_status(self, status: bool):
        self.is_watched = status

    def set_rating(self, user_rating: BaseFilmComplexRating[BaseRatingScale], serialize_for_json):
        self.user_rating = serialize_for_json(user_rating)

    film: Optional[Film] = Relationship(
        back_populates=None,
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    __table_args__ = (
        PrimaryKeyConstraint("filmid", "userid"),
        ForeignKeyConstraint(
            ["filmid"],
            ["films.filmid"],
        )
    )
