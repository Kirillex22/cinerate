from functools import wraps
from typing import List, Callable, Union, Optional

from src.infrastructure.repositories.core.base_playlist_repository import BasePlaylistRepository
from src.domain.entities.film import FilmBase
from src.domain.entities.playlist import Playlist, PlaylistItemPreview
from src.domain.entities.user import User
from src.web.models.playlists import CreatePlaylistModel, AccessModel, PlaylistSearchFilters, FiltersFields, \
    PrivatePlaylistSearchFilters
from src.services.playlist.exceptions import UserDoesntHavePermissionException, \
    PlaylistsNotFoundException, EmptyPlaylistException, CollaboratorAlreadyExistsException, \
    CollaboratorDoesNotExistException


def require_all_filters(*required_attrs: str):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            filters_obj = next((arg for arg in args if isinstance(arg, PlaylistSearchFilters)), None)
            missing = [attr for attr in required_attrs if not getattr(filters_obj, attr, None)]

            if len(missing) > 0:
                raise ValueError(f"Поля {missing} должны быть заданы.")

            return func(*args, **kwargs)

        return wrapper

    return decorator


class PlaylistService:
    def __init__(self, repository: BasePlaylistRepository):
        self._repository = repository

    def create_playlist(self, user: User, create_data: CreatePlaylistModel) -> str:
        if create_data.gen_attrs is not None:
            create_data.description = create_data.gen_attrs.generate_description()

        return self._repository.create_playlist(user, create_data)

    def get_playlists(self, filters: PlaylistSearchFilters, access_model: Optional[AccessModel] = None) -> Union[
        List[Playlist], Playlist]:

        if not access_model:  # если не передается модель доступа, то производится общий поиск по плейлистам -> нет необходимости проверки прав -> получаем только публичные плейлисты из поиска
            filters.only_public = True
            playlists = self._repository.get_playlists(filters)

            if not playlists:
                raise PlaylistsNotFoundException(AccessModel('CURRENT'), filters)  # костыль

            return playlists

        if access_model:
            if filters.playlistid:
                playlist = self._repository.get_playlist_by_id(filters.playlistid)

                if not playlist:
                    raise PlaylistsNotFoundException(access_model, filters)

                if access_model.is_owner(playlist) or access_model.is_collaborator(playlist) or playlist.is_public:
                    return playlist

                raise PlaylistsNotFoundException(access_model, filters)

            if not filters.target_user:
                filters.target_user = access_model.current_user
                filters = PrivatePlaylistSearchFilters(**filters.model_dump())

            playlists = self._repository.get_playlists(filters)

            if not playlists:
                raise PlaylistsNotFoundException(access_model, filters)

            if not isinstance(playlists, list):
                playlists = [playlists]

            filtered_playlists: List[Playlist] = []

            for playlist in playlists:
                if access_model.is_owner(playlist) or access_model.is_collaborator(playlist) or playlist.is_public:
                    filtered_playlists.append(playlist)

            if len(filtered_playlists) > 0:
                return filtered_playlists

            raise PlaylistsNotFoundException(access_model, filters)

    @require_all_filters(FiltersFields.PLAYLISTID)
    def remove_playlist(self, access_model: AccessModel, filters: PlaylistSearchFilters) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if access_model.is_owner(playlist):
            fixed_filters = filters.left_only_playlistid()
            self._repository.remove_playlist(fixed_filters)
            return

        raise UserDoesntHavePermissionException(access_model, filters, "remove")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def add_to_playlist(self, access_model: AccessModel, filters: PlaylistSearchFilters, target_film: FilmBase) -> None:

        playlist = self._repository.get_playlists(filters)

        if access_model.is_collaborator(playlist) or access_model.is_owner(playlist):
            fixed_filters = filters.left_only_playlistid()
            self._repository.add_to_playlist(fixed_filters, target_film, access_model.current_user)
            return

        raise UserDoesntHavePermissionException(access_model, filters, f"add film {target_film.filmid} to")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def remove_from_playlist(self, access_model: AccessModel, filters: PlaylistSearchFilters,
                             target_film: FilmBase) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)
        playlist_item = self._repository.get_playlist_item(filters, target_film)

        if access_model.is_creator(playlist_item) or access_model.is_owner(playlist):
            fixed_filters = filters.left_only_playlistid()
            self._repository.remove_playlist_item(fixed_filters, target_film)
            return

        raise UserDoesntHavePermissionException(access_model, filters, f"remove film {target_film.filmid} from")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def set_publicity(self, access_model: AccessModel, filters: PlaylistSearchFilters, publicity: bool) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if access_model.is_owner(playlist):
            playlist.is_public = publicity
            self._repository.update_playlist(playlist)
            return

        raise UserDoesntHavePermissionException(access_model, filters, "change publicity of")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def set_name(self, access_model: AccessModel, filters: PlaylistSearchFilters, name: str) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if access_model.is_owner(playlist):
            playlist.name = name
            self._repository.update_playlist(playlist)
            return

        raise UserDoesntHavePermissionException(access_model, filters, "change name of")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def set_description(self, access_model: AccessModel, filters: PlaylistSearchFilters, description: str) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if access_model.is_owner(playlist):
            playlist.description = description
            self._repository.update_playlist(playlist)
            return

        raise UserDoesntHavePermissionException(access_model, filters, "change name of")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def add_collaborator(self, access_model: AccessModel, filters: PlaylistSearchFilters, collaborator: User) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if access_model.is_owner(playlist):

            if collaborator.userid in playlist.collaborators:
                raise CollaboratorAlreadyExistsException(
                    f'Collaborator {collaborator.userid} already exists for playlist {playlist}')

            playlist.collaborators.append(collaborator.userid)
            self._repository.update_playlist(playlist)
            return

        raise UserDoesntHavePermissionException(access_model, filters, "add collaborator to")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def remove_from_collaborators(self, access_model: AccessModel, filters: PlaylistSearchFilters,
                                  collaborator: User) -> None:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if access_model.is_owner(playlist):

            if collaborator.userid not in playlist.collaborators:
                raise CollaboratorDoesNotExistException(
                    f'Collaborator {collaborator.userid} does not exists for playlist {playlist}')

            playlist.collaborators.remove(collaborator.userid)
            self._repository.update_playlist(playlist)
            return

        raise UserDoesntHavePermissionException(access_model, filters, "remove collaborator from")

    @require_all_filters(FiltersFields.PLAYLISTID)
    def get_playlist_content(self, access_model: AccessModel, filters: PlaylistSearchFilters) -> List[
        PlaylistItemPreview]:

        playlist = self._repository.get_playlist_by_id(filters.playlistid)

        if (playlist.gen_attrs is not None) and (access_model.is_owner(playlist)):
            filters.target_user = access_model.current_user
            self._repository.autofill_playlist(filters)

        if access_model.is_owner(playlist) or access_model.is_collaborator(playlist) or playlist.is_public:
            fixed_filters = filters.left_only_playlistid()
            content = self._repository.get_playlist_content(fixed_filters)

            if content is None:
                raise EmptyPlaylistException(filters)

            return content

        raise UserDoesntHavePermissionException(access_model, filters, "get content from")
