from fastapi_sdk.exceptions.exceptions import AppException
from fastapi_sdk.exceptions.handlers import app_exception_handler
from fastapi_sdk.exceptions.handlers import fastapi_exception_error_handler
from fastapi_sdk.exceptions.handlers import request_validation_exception_handler
from fastapi_sdk.exceptions.handlers import unexpected_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

exception_handler_mapping = {
    RequestValidationError: request_validation_exception_handler,
    AppException: app_exception_handler,
    HTTPException: fastapi_exception_error_handler,
    Exception: unexpected_exception_handler,
}
