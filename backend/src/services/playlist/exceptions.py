from src.web.models.playlists import AccessModel, PlaylistSearchFilters


class PlaylistServiceException(Exception):
    pass


class UserDoesntHavePermissionException(PlaylistServiceException):
    code = "NOT ENOUGH RIGHTS"

    def __init__(self, access_model: AccessModel, filters: PlaylistSearchFilters, action: str):
        super().__init__(
            f"User {access_model.current_user} can't {action} playlist {filters.playlistid} belonging user {filters.target_user}.")


class PlaylistsNotFoundException(PlaylistServiceException):
    code = "NOT FOUND"

    def __init__(self, access_model: AccessModel, filters: PlaylistSearchFilters):
        super().__init__(
            f"User {filters.target_user} doesn't have playlist matching filters {filters}"
        )


class EmptyPlaylistException(PlaylistServiceException):
    code = "EMPTY"

    def __init__(self, filters: PlaylistSearchFilters):
        super().__init__(
            f"Playlist {filters.playlistid} is empty"
        )


class CollaboratorAlreadyExistsException(PlaylistServiceException):
    pass


class CollaboratorDoesNotExistException(PlaylistServiceException):
    pass
