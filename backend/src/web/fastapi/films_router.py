from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException

from src.dependencies import get_current_user, get_film_service_dep
from src.domain.entities.film import FilmExtended, FilmPreview, FilmBase, FilmPersonal
from src.domain.entities.user import User
from src.services.film.exceptions import (
    EmptyListException, NotFoundLocalException, NotFoundExternalException,
    AlreadyWatchedException, DoesNotExistException
)
from src.web.models.film_rating import BaseFilmComplexRating, BaseRatingScale
from src.web.models.search_filters import BaseSearchingFilters, BaseApiSearchingFilters

films_router = APIRouter(
    prefix='/films',
    tags=['films']
)


@films_router.post("/local/get", response_model=Union[FilmExtended, List[FilmExtended]])
async def get_film_details(
        film: FilmPersonal,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        return await film_service.get(user=user, film_to_get=film)
    except DoesNotExistException as e:
        raise HTTPException(status_code=400, detail=str(e))


@films_router.post("/unwatched")
def add_to_unwatched(
        film: FilmExtended,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        film_service.add_to_unwatched(user, film)
        return {"detail": "Added to unwatched"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@films_router.get("/list", response_model=List[FilmPreview])
def get_unwatched(
        watched: bool,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        return film_service.get_list(user, is_watched=watched)
    except EmptyListException as e:
        raise HTTPException(status_code=404, detail=str(e))


@films_router.post("/search/local", response_model=List[FilmPreview])
def local_search(
        filters: BaseSearchingFilters,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        return film_service.local_search_by_filters(user, filters)
    except NotFoundLocalException as e:
        raise HTTPException(status_code=404, detail=str(e))


@films_router.post("/search/external", response_model=List[FilmPreview])
async def external_search(
        filters: BaseApiSearchingFilters,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        return await film_service.external_search_by_filters(filters, user=user)
    except NotFoundExternalException as e:
        raise HTTPException(status_code=404, detail=str(e))


@films_router.post("/external", response_model=Union[FilmExtended, List[FilmExtended]])
async def external_get(
        film: FilmPersonal,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        return await film_service.get(user, film)
    except NotFoundExternalException as e:
        raise HTTPException(status_code=404, detail=str(e))


@films_router.post("/watch-status")
def set_watch_status(
        film: FilmBase,
        status: bool,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        film_service.set_watch_status(user, film, status)
        return {"detail": "Status updated"}
    except AlreadyWatchedException as e:
        raise HTTPException(status_code=400, detail=str(e))


@films_router.post("/rate")
def set_rate(
        film: FilmBase,
        rating: BaseFilmComplexRating[BaseRatingScale],
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        film_service.set_rate(user, film, rating)
        return {"detail": "Rating set"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@films_router.delete("/")
def remove_film(
        film: FilmBase,
        user: User = Depends(get_current_user),
        film_service=Depends(get_film_service_dep)
):
    try:
        film_service.remove(user, film)
        return {"detail": "Removed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
