"""Generic dependencies"""
# pylint: disable=E0401

from datetime import datetime, timedelta

from typing import Annotated
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
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


def get_user_by_username(username: str) -> User | None:
    """
    Retrieves a user from the database by their username.

    args:
        username (str): The username of the user to retrieve.

    returns:
        User: The user object retrieved from database, or
        None if the user is not found.
    """
    try:
        with get_unit_of_work() as uow:
            user_service = UserService(uow.session)
            user = user_service.get_user_by_username(username)
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


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Get the current user based on the provided token
    """
    # Raise an exception if the credentials cannot be validated
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token to extract the payload
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        # Get the username from the payload
        username = payload.get("sub")
        # Raise an exception if the username is not found
        if username is None:
            raise credentials_exception
    except JWTError as e:
        # Raise an exception if there is a JWT error
        raise credentials_exception from e
    # Get the user based on the username
    user = get_user_by_email(username)
    # Raise an exception if the user is not found
    if user is None:
        raise credentials_exception
    # Return the user
    return user
