from enum import Enum
from typing import Any
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from fastapi import status
from pydantic import BaseModel
from pydantic.generics import GenericModel
from starlette.responses import Response

AnyResponseType = TypeVar('AnyResponseType')


class ResponseStatus(int, Enum):
    """Response status enum."""

    OK = 0
    SERVER_ERROR = 1000
    UNKNOWN_CLIENT_ERROR = 4000
    NOT_FOUND = 4001
    VALIDATION_ERROR = 4002
    USER_ALREADY_EXISTS = 4003
    USER_NOT_FOUND = 4004
    CREDENTIALS_ERROR = 4005
    INVALID_ACCESS_OR_REFRESH_TOKEN = 4006
    UNAUTHORIZED = 4007
    TOO_MANY_PASSWORD_RECOVERY_ATTEMPTS = 4008
    INVALID_PASSWORD_RECOVERY_CODE = 4009

    @staticmethod
    def from_status_code(status_code: int) -> 'ResponseStatus':
        """Create response status from status code."""

        if status_code == status.HTTP_404_NOT_FOUND:
            return ResponseStatus.NOT_FOUND
        elif status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            return ResponseStatus.VALIDATION_ERROR
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            return ResponseStatus.UNAUTHORIZED

        if 200 <= status_code <= 299:
            return ResponseStatus.OK
        elif 400 <= status_code <= 499:
            return ResponseStatus.UNKNOWN_CLIENT_ERROR
        elif 500 <= status_code <= 599:
            return ResponseStatus.SERVER_ERROR
        return ResponseStatus.SERVER_ERROR


class FieldErrorSchema(BaseModel):
    """Field error schema."""

    field: str
    message: str


FieldErrorsSchema = List[FieldErrorSchema]


class DefaultResponseSchema(GenericModel, Generic[AnyResponseType]):
    custom_code: ResponseStatus = ResponseStatus.OK
    message: Optional[str] = None
    details: Optional[FieldErrorsSchema] = None
    data: Optional[AnyResponseType] = None


class DefaultResponse(Response):
    media_type = 'application/json'

    def __init__(
        self,
        *args,
        custom_code: int = ResponseStatus.OK,
        message: Optional[str] = None,
        details: Optional[FieldErrorsSchema] = None,
        **kwargs,
    ) -> None:
        self.message = message
        self.details = details
        self.custom_code = custom_code
        super().__init__(*args, **kwargs)

    def render(self, content: Any) -> bytes:  # noqa: ANN401
        return (
            DefaultResponseSchema(
                custom_code=self.custom_code,
                message=self.message,
                details=self.details,
                data=content,
            )
            .json()
            .encode()
        )
