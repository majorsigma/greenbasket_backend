"""Generic dependencies"""
# pylint: disable=E0401

from datetime import datetime, timedelta

# from typing import Annotated
# from fastapi import Depends, status
# from fastapi.exceptions import HTTPException
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from app.exceptions.users import UserNotFoundException
from app.models import User
from app.services.user_service import UserService
from app.unit_of_work import UnitOfWork
from app.utils import GBLogger

SECRET_KEY = "6bd30698838f912a60fc3a57b51da2132d1f2ee046b82ae07d75b21\
64b39ffaeeadd44c7442fa39b7a70799b506563dad8370417b29dcb457ff2f1d68a34fc60"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
logger = GBLogger("Dependencies")


def get_unit_of_work():
    """
    Creates and returns a new instance of UnitOfWork class.
    """
    uow = UnitOfWork()
    return uow


def get_user_by_email(email: str) -> User | None:
    """
    Retrieves a user from the database by their email.

    args:
        email (str): The email of the user to retrieve.

    returns:
        database.User: The user object retrieved from database, or
        None if the user is not found.
    """
    try:
        with get_unit_of_work() as uow:
            user_service = UserService(uow.session)
            user = user_service.get_user_by_email(email)
            return user
    except Exception as e:
        raise UserNotFoundException from e


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generate an access token based on the provided data.

    Args:
        data (dict): A dictionary containing the data to encode into the access token.
        expires_delta (timedelta | None, optional): The expiration time of the access token.
        Defaults to None.

    Returns:
        str: The encoded access token.

    Raises:
        None

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
