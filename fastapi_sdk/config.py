from typing import TypeVar
import databases

ModelType: TypeVar
db_connection: databases.core.Database
DEFAULT_DATETIME_FORMAT: str
ENVIRONMENT: str = 'dev'


def init_sdk(
    model_type: TypeVar,
    database_connection: databases.core.Database,
    default_datetime_format: str,
    environment: str = 'dev',
) -> None:
    global ModelType
    global db_connection
    global DEFAULT_DATETIME_FORMAT
    global ENVIRONMENT

    ModelType = model_type
    db_connection = database_connection
    DEFAULT_DATETIME_FORMAT = default_datetime_format
    ENVIRONMENT = environment

