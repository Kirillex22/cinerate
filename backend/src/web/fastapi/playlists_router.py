from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException

from src.domain.entities.film import FilmBase
from src.domain.entities.playlist import Playlist, PlaylistItemPreview
from src.domain.entities.user import User
from src.services.playlist.exceptions import (
    PlaylistsNotFoundException,
    UserDoesntHavePermissionException,
    EmptyPlaylistException,
)
from src.web.models.playlists import CreatePlaylistModel, PlaylistSearchFilters
from src.services.playlist.service import PlaylistService

from src.dependencies import (
    get_playlist_service_dep,
    get_current_user,
    build_access_model,
)

playlists_router = APIRouter(
    prefix='/playlists',
    tags=['playlists']
)


@playlists_router.post("/create", response_model=str)
def create_playlist(
        create_data: CreatePlaylistModel,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    return playlist_service.create_playlist(user, create_data)


@playlists_router.post("/get", response_model=Union[List[Playlist], Playlist])
def get_playlists(
        filters: PlaylistSearchFilters,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        return playlist_service.get_playlists(filters, access_model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PlaylistsNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@playlists_router.post("/search", response_model=Union[List[Playlist], Playlist])
def search_playlists(
        filters: PlaylistSearchFilters,
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        return playlist_service.get_playlists(filters)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PlaylistsNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@playlists_router.delete("/remove")
def remove_playlist(
        filters: PlaylistSearchFilters,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.remove_playlist(access_model, filters)
        return {"detail": "Playlist removed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/add")
def add_to_playlist(
        filters: PlaylistSearchFilters,
        target_film: FilmBase,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.add_to_playlist(access_model, filters, target_film)
        return {"detail": f"Film {target_film.filmid} added to playlist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/remove-film")
def remove_from_playlist(
        filters: PlaylistSearchFilters,
        target_film: FilmBase,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.remove_from_playlist(access_model, filters, target_film)
        return {"detail": f"Film {target_film.filmid} removed from playlist"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/set-publicity")
def set_publicity(
        filters: PlaylistSearchFilters,
        publicity: bool,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.set_publicity(access_model, filters, publicity)
        return {"detail": f"Playlist publicity set to {publicity}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/set-name")
def set_name(
        filters: PlaylistSearchFilters,
        name: str,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.set_name(access_model, filters, name)
        return {"detail": f"Playlist name set to {name}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/set-description")
def set_description(
        filters: PlaylistSearchFilters,
        description: str,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.set_description(access_model, filters, description)
        return {"detail": f"Playlist description set to {description}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/add-collaborator")
def add_collaborator(
        filters: PlaylistSearchFilters,
        collaborator: User,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.add_collaborator(access_model, filters, collaborator)
        return {"detail": f"Collaborator {collaborator.userid} added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/remove-collaborator")
def remove_from_collaborators(
        filters: PlaylistSearchFilters,
        collaborator: User,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        playlist_service.remove_from_collaborators(access_model, filters, collaborator)
        return {"detail": f"Collaborator {collaborator.userid} removed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@playlists_router.post("/content", response_model=List[PlaylistItemPreview])
def get_playlist_content(
        filters: PlaylistSearchFilters,
        user: User = Depends(get_current_user),
        playlist_service: PlaylistService = Depends(get_playlist_service_dep)
):
    try:
        access_model = build_access_model(user)
        return playlist_service.get_playlist_content(access_model, filters)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except EmptyPlaylistException as e:
        raise HTTPException(status_code=404, detail=str(e))
