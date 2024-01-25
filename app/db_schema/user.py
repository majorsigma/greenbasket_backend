"""Schemas for the database"""

from pydantic import BaseModel


class User(BaseModel):
    """Model for outputting user information"""

    uid: str
    username: str
    email: str
    date_of_birth: str
    is_active: bool
    is_2fa_enabled: bool
    is_verified: bool | None
    is_online: bool
    address: str
    state: str | None = None
    lga: str | None = None
    created_at: str
    updated_at: str


class UserInput(BaseModel):
    """Model for creating a new user"""

    username: str
    password: str
    email: str
    date_of_birth: str
    address: str | None


class LoginInput(BaseModel):
    """Model for logging in a user"""

    email: str
    password: str


class LoginResponse(BaseModel):
    """Model for logging in a user"""

    status: str
    access_token: str
    user: User


class UserVerification(BaseModel):
    """Model for verifying a user"""

    user_email: str
    verification_code: str
