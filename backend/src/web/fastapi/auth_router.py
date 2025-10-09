from fastapi import APIRouter, Depends, HTTPException, status, Response

from src.dependencies import get_auth_service_dep
from src.domain.entities.user import UserRegisterForm
from src.services.auth.service import AuthService

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@auth_router.post("/token")
async def login_for_access_token(
        login: str,
        password: str,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service_dep)
) -> str:
    user = auth_service.authenticate_user(login, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(
        data={
            "sub": user.userid,
            "role": user.role,
        }
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return access_token


@auth_router.post("/register")
async def register_user(
        register_form: UserRegisterForm,
        auth_service: AuthService = Depends(get_auth_service_dep)
):
    try:
        auth_service.register_user(register_form)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot register {e}",
        )
