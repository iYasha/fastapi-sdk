from enum import Enum
from typing import Optional

from pydantic import BaseSettings


class Environment(str, Enum):
    PROD = 'production'
    RC = 'rc'
    STAGE = 'stage'
    DEV = 'dev'


class Settings(BaseSettings):
    """
    Настройки из переменных окружения
    """

    # Base configuration for the application.
    ENVIRONMENT: Optional[Environment] = None

    # API configuration.
    DEFAULT_DATETIME_FORMAT: str = '%Y-%m-%dT%H:%M:%S%z'


settings = Settings()
