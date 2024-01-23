"""Module for routing user related endpoints"""
# pylint: disable=E0401

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.db_schema.user import UserInput, User, LoginInput
from app.dependencies import (
    UnitOfWork,
    get_user_by_email,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.exceptions.users import UserAlreadyExistsException, UserRegistrationException
# from app import models
from app.utils import GBLogger
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])
logger = GBLogger("UserRouter")


def authenticate_user(username: str, password: str) -> User | None:
    """
    Authenticates a user using the provided username and password.

    Parameters:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        Union[bool, User]: Returns the authenticated user if successful,
        or False if authentication fails.
    """
    user = get_user_by_email(username)
    if not user:
        return None
    if not UserService.verify_password(password, user.password):
        return None
    return user


@router.get("/users")
def get_users() -> dict:
    """Get all users"""
    with UnitOfWork() as uow:
        logger.log_debug(f"UOW's session {dir(uow.session)}")
        user_service = UserService(uow.session)
        users = user_service.get_all_users()
        return {"users": users}


@router.post("/user/register")
def register_user(user_data: Annotated[UserInput, Body()]) -> JSONResponse:
    """Register a new user"""
    with UnitOfWork() as uow:
        try:
            user_service = UserService(uow.session)
            db_user = user_service.register_user(user_data)
            user = User(**db_user.dict())
            return JSONResponse({"status": "success", "user": user.dict()})
        except UserAlreadyExistsException:
            return JSONResponse(
                {"status": "error", "message": "User already exists"},
                status_code=status.HTTP_409_CONFLICT,
            )
        except UserRegistrationException as e:
            logger.log_error(f"Error creating a user: {e}")
            return JSONResponse(
                {"status": "error", "message": "Error creating a user"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@router.post("/user/login", description="Logs user in")
async def login(user_data: Annotated[LoginInput, Body()]):
    """
    Logs in a user and returns an access token.

    Parameters:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): The form data containing
        the username and password.

    Returns:
        dict: A dictionary containing the access token and token type.
            - access_token (str): The access token.
            - token_type (str): The token type.
    """
    user_dict = user_data.dict()
    email_address = user_dict.get("email")
    password = user_dict.get("password")
    db_user = authenticate_user(email_address, password)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    user = User(**db_user.dict())
    return JSONResponse(
        {
            "status": "success",
            "access_token": access_token,
            "user": user.dict(),
        }
    )
