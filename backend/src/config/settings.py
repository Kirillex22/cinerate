import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum

from src.domain.entities.user import UserRegisterForm


class JWTAlgorithm(str, Enum):
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"
    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"
    NONE = "none"


class RatingScale(BaseModel):
    VALUES: List[str]


class ExternalApiSettings(BaseSettings):
    API_BASE_URL: str
    API_ACCESS_TOKEN: str


class PostgresSettings(BaseSettings):
    USERNAME: str
    PASSWORD: str
    DB_NAME: str
    SCHEMA: str
    HOST: str
    PORT: Optional[int] = None

    def make_url(self):
        if not self.PORT:
            return f"postgresql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}/{self.DB_NAME}"
        return f"postgresql://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}"


class SecuritySettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: Optional[JWTAlgorithm] = JWTAlgorithm.HS256
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def algorithm(self) -> str:
        return self.ALGORITHM.value if self.ALGORITHM else None


class SettingsEnv(BaseSettings):
    YAML_CONFIG_PATH: str = './config.yaml'  # путь по умолчанию

    class Config:
        env_file = '.env'  #


class AppSettings(BaseSettings):
    APP_NAME: Optional[str] = 'cinerate-api'
    API_VERSION: Optional[int] = 1
    ORIGINS: Optional[list[str]] = ['*']
    POSTGRES_SETTINGS: Optional[PostgresSettings] = None
    EXTERNAL_API_SETTINGS: Optional[ExternalApiSettings] = None
    SECURITY_SETTINGS: Optional[SecuritySettings] = None
    ADMIN_USER: Optional[UserRegisterForm] = None
    RATING_SCALE: Optional[RatingScale] = None

    @classmethod
    def from_yaml(cls, path_to_config: Optional[str] = None):
        if path_to_config is None:
            env = SettingsEnv()
            path_to_config = env.YAML_CONFIG_PATH

        with open(path_to_config, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            return cls(**config_data)
