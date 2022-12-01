from typing import Optional

from fastapi_sdk.responses import FieldErrorSchema
from fastapi_sdk.responses import FieldErrorsSchema
from fastapi_sdk.responses import ResponseStatus

__all__ = ['AppException', 'make_error']


class AppException(Exception):
    """Базовый класс ошибок"""

    app_code: ResponseStatus
    message: Optional[str]
    field_errors: Optional[FieldErrorsSchema]

    def __init__(
        self,
        custom_code: ResponseStatus,
        message: Optional[str] = None,
        field_errors: FieldErrorsSchema = None,
    ) -> None:
        self.message = message
        self.custom_code = custom_code
        self.field_errors = field_errors


def make_error(
    custom_code: ResponseStatus,
    message: Optional[str] = None,
    **details,
) -> AppException:
    """Raise HTTP exception with custom response."""

    return AppException(
        custom_code=custom_code,
        message=message,
        field_errors=[FieldErrorSchema(field=field, message=details[field]) for field in details],
    )
