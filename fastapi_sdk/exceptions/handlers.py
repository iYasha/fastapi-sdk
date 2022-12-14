import traceback
from typing import List

from fastapi_sdk.config import settings, Environment
from fastapi_sdk.exceptions.exceptions import AppException
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request

from fastapi_sdk.responses import DefaultResponse
from fastapi_sdk.responses import FieldErrorSchema
from fastapi_sdk.responses import ResponseStatus


def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
    language: str = 'en',
) -> DefaultResponse:
    """Обработчик ошибок валидации параметров запроса - ошибки от Pydantic"""
    field_errors: List[FieldErrorSchema] = []

    for error in exc.errors():
        field = list(map(str, error.get('loc', '')))

        if error['type'] == 'value_error.jsondecode':
            field_errors.append(FieldErrorSchema(field='body', message='Invalid JSON'))
            break

        if 'body' in field:
            field.remove('body')

        field_string = ', '.join(field)
        message = error.get('msg', '')
        field_errors.append(FieldErrorSchema(field=field_string, message=message))

    return DefaultResponse(
        custom_code=ResponseStatus.from_status_code(status.HTTP_422_UNPROCESSABLE_ENTITY),
        message='Validation error',
        details=field_errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


def unexpected_exception_handler(request: Request, exc: Exception) -> DefaultResponse:
    """Обработчик любых непредвиденных и необработанных ошибок"""

    error_message = 'Возникла непредвиденная ошибка. Пожалуйста, обратитесь к администратору.'
    if settings.ENVIRONMENT == Environment.DEV:
        error_message = ''.join(
            traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__),
        )

    return DefaultResponse(
        custom_code=ResponseStatus.from_status_code(status.HTTP_500_INTERNAL_SERVER_ERROR),
        message=error_message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def fastapi_exception_error_handler(request: Request, exc: HTTPException) -> DefaultResponse:
    """Обработчик ошибок FastAPI"""

    return DefaultResponse(
        custom_code=ResponseStatus.from_status_code(exc.status_code),
        message=exc.detail,
        details=[],
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def app_exception_handler(request: Request, exc: AppException) -> DefaultResponse:
    """Обработчик ошибок приложения"""

    return DefaultResponse(
        custom_code=exc.custom_code,
        message=exc.message,
        details=exc.field_errors,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
