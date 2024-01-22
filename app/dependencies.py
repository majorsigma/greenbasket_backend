"""Generic dependencies"""
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, status
from jose import jwt, JWTError
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models import User
from app.services.user_service import UserService
from app.unit_of_work import UnitOfWork
from app.utils import GBLogger

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
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
        logger.log_error(f"Exeception: {e}")
        return None