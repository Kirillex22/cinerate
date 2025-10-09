import uuid

from sqlalchemy import literal, func, or_
from src.domain.entities.user import User
from src.web.models.playlists import PlaylistSearchFilters, PrivatePlaylistSearchFilters
from src.infrastructure.repositories.impl.postgres.playlist_repository.orm import PlaylistORM


class PlaylistQueryBuilder:
    def __init__(self, base_query):
        self.query = base_query
        self.selection_by_collaborators = False

    def apply_all(self, filters: PlaylistSearchFilters):
        if isinstance(filters, PrivatePlaylistSearchFilters):
            self.selection_by_collaborators = True

        for field, value in filters.model_dump(exclude_none=True).items():
            self.apply_filter(field, value)
        return self

    def apply_filter(self, field: str, value: any):
        method_name = f"filter_by_{field}"
        method = getattr(self, method_name, None)
        if method:
            self.query = method(value)

    def filter_by_playlistid(self, value: str):
        uuid_value = uuid.UUID(value)
        return self.query.where(PlaylistORM.playlistid == uuid_value)

    def filter_by_name(self, value: str):
        return self.query.where(PlaylistORM.name.ilike(f"%{value}%"))

    def filter_by_only_public(self, value: bool):
        return self.query.where(PlaylistORM.is_public == value)

    def filter_by_target_user(self, user: dict):
        user = User(**user)
        if self.selection_by_collaborators:
            return self.query.where(
                or_(
                    PlaylistORM.collaborators.any(user.userid),
                    PlaylistORM.userid == user.userid
                )

            )
        return self.query.where(PlaylistORM.userid == user.userid)

    def filter_by_entries_as_collaborator(self, value: bool):
        return self.query.where(literal(value) == func.any(PlaylistORM.collaborators))

    def build(self):
        return self.query
