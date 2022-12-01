from typing import TypeVar
import databases

ModelType: TypeVar
db_connection: databases.core.Database
DEFAULT_DATETIME_FORMAT: str


def init_sdk(model_type: TypeVar, database_connection: databases.core.Database, default_datetime_format: str) -> None:
    global ModelType
    global db_connection
    global DEFAULT_DATETIME_FORMAT
    ModelType = model_type
    db_connection = database_connection
    DEFAULT_DATETIME_FORMAT = default_datetime_format

