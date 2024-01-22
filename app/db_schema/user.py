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
    is_online: bool
    address: str
    created_at: str
    updated_at: str

class UserInput(BaseModel):
    """Model for creating a new user"""
    username: str
    password: str
    email: str
    date_of_birth: str
    address: str | None
