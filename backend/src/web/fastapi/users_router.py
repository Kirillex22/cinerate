from datetime import datetime
from typing import List
from fastapi import Depends, HTTPException, APIRouter

from src.dependencies import build_user_access_model, get_current_user, get_social_service_dep
from src.domain.entities.user import User, RoleEnum, StatusEnum, UserPublic, UserPreview, UserHistoryModel
from src.services.social.exceptions import UserNotFoundException
from src.services.playlist.exceptions import UserDoesntHavePermissionException
from src.web.models.users import UserSearchingFilters

users_router = APIRouter(
    prefix='/users',
    tags=['users']
)


@users_router.get("/current", response_model=User)
def get_current(user: User = Depends(get_current_user)):
    return user


@users_router.get("/search", response_model=List[UserPreview])
def search_users(
        username: str = None,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    access_model = build_user_access_model(user)
    filters = UserSearchingFilters(username=username)
    try:
        return social_service.search_users(access_model, filters)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.get("/{user_id}", response_model=UserPublic)
def get_user(
        user_id: str,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    filters = UserSearchingFilters(target_user=User(userid=user_id, role=user.role, status=user.status))
    access_model = build_user_access_model(user)
    try:
        return social_service.get_user(access_model, filters)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.get("/{user_id}/subscribers", response_model=List[UserPreview])
def get_subscribers(
        user_id: str,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    filters = UserSearchingFilters(target_user=User(userid=user_id, role=user.role, status=user.status))
    access_model = build_user_access_model(user)
    try:
        return social_service.get_subscribers(access_model, filters)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.get("/{user_id}/subscribes", response_model=List[UserPreview])
def get_subscribes(
        user_id: str,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    filters = UserSearchingFilters(target_user=User(userid=user_id, role=user.role, status=user.status))
    access_model = build_user_access_model(user)
    try:
        return social_service.get_subscribes(access_model, filters)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.get("/{user_id}/actions", response_model=List[UserHistoryModel])
def get_actions_history(
        user_id: str,
        date_start: datetime,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    filters = UserSearchingFilters(target_user=User(userid=user_id, role=user.role, status=user.status))
    access_model = build_user_access_model(user)
    try:
        return social_service.get_actions_history(access_model, filters, date_start)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.post("/{user_id}/subscribe")
def subscribe(
        user_id: str,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    filters = UserSearchingFilters(target_user=User(userid=user_id, role=RoleEnum.USER, status=StatusEnum.PUBLIC))
    try:
        social_service.subscribe(user, filters)
        return {"message": "Subscription successful"}
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.post("/{user_id}/unsubscribe")
def unsubscribe(
        user_id: str,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    filters = UserSearchingFilters(target_user=User(userid=user_id, role=user.role, status=user.status))
    try:
        social_service.unsubscribe(user, filters)
        return {"message": "Unsubscription successful"}
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))


@users_router.put("/{user_id}", response_model=UserPublic)
def update_profile(
        user_id: str,
        target_user: UserPublic,
        user: User = Depends(get_current_user),
        social_service=Depends(get_social_service_dep)
):
    access_model = build_user_access_model(user)
    target_user.userid = user_id
    try:
        social_service.update_profile(access_model, target_user)
        filters = UserSearchingFilters(target_user=target_user)
        return social_service.get_user(access_model, filters)
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserDoesntHavePermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))
