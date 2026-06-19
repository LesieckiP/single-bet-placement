from enum import StrEnum

from pydantic import BaseModel


class AuthErrorType(StrEnum):
    MISSING_USER_ID = "missing_user_id"
    INVALID_USER_ID = "invalid_user_id"


class ErrorResponse(BaseModel):
    error: str
    message: str


class AuthErrorResponse(BaseModel):
    error: AuthErrorType
