import jwt
from datetime import timedelta, datetime, timezone
from typing import Optional

from src.config.settings import SecuritySettings
from src.infrastructure.repositories.core.base_social_repository import BaseSocialRepository
from src.domain.entities.user import User, UserRegisterForm, UserRegisterPrepared
from src.services.social.exceptions import UserNotExistsException


def extract_token(token_str: str | None) -> str:
    if not token_str:
        raise ValueError("Token is missing")

    token_str = token_str.strip()
    prefix = "bearer "
    if token_str.lower().startswith(prefix):
        return token_str[len(prefix):].strip()
    return token_str


class AuthService:
    def __init__(self, security_config: SecuritySettings, social_repository: BaseSocialRepository, pwd_context):
        self._security_config = security_config
        self._social_repository = social_repository
        self._pwd_context = pwd_context

    def verify_password(self, plain_password, hashed_password):
        return self._pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self._pwd_context.hash(password)

    def authenticate_user(self, login: str, password: str):
        user = self._social_repository.get_user(None, login=login)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._security_config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self._security_config.SECRET_KEY,
            algorithm=self._security_config.algorithm
        )
        return encoded_jwt

    def get_user_by_access_token(self, token: str) -> Optional[User]:
        token = extract_token(token)
        payload = jwt.decode(
            token,
            self._security_config.SECRET_KEY,
            algorithms=[self._security_config.algorithm],
        )
        userid = payload.get("sub")
        role = payload.get("role")

        if userid is None:
            raise jwt.InvalidTokenError

        user = User(userid=userid, role=role)

        self._social_repository.get_user(user)
        if user is None:
            raise UserNotExistsException()
        return user

    def register_user(self, user: UserRegisterForm, is_admin: bool = False) -> None:
        password_hash = self.get_password_hash(user.password)
        user_register_prep = UserRegisterPrepared(
            login=user.login,
            hashed_password=password_hash,
            email=user.email,
            birth_date=user.birth_date,
        )
        self._social_repository.create_user(user_register_prep, is_admin=is_admin)
