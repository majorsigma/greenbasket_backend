"""Module for routing user related endpoints"""
# pylint: disable=E0401, E0611

import smtplib
from datetime import timedelta
from typing import Annotated
from email.mime.text import MIMEText
import pyotp
from fastapi import APIRouter, Body, Query, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.db_schema.user import (
    UserInput,
    User,
    LoginInput,
    LoginResponse,
    UserVerification,
)
from app.dependencies import (
    UnitOfWork,
    get_user_by_email,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.exceptions.users import UserAlreadyExistsException, UserRegistrationException

from app import models
from app.services.user_service import UserService
from app.utils import GBLogger
from dotenv import dotenv_values

router = APIRouter(prefix="/auth", tags=["auth"])
env_vars = dotenv_values(".env")
SMTP_SERVER = str(env_vars.get("SMTP_SERVER"))
SMTP_PORT = str(env_vars.get("SMTP_PORT"))
SMTP_USER = str(env_vars.get("SMTP_USER"))
SMTP_PASSWORD = str(env_vars.get("SMTP_PASSWORD"))
TOTP_SECRET = str(env_vars.get("TOTP_SECRET"))

logger = GBLogger("UserRouter")

totp = pyotp.TOTP(str(TOTP_SECRET), interval=60, issuer="GreenBasket")


def send_verification_email(email, verification_code) -> bool:
    """Sends a verfication email to the user"""
    msg = MIMEText(
        f"Your verification code is: {verification_code}",
        "html",
    )

    msg["Subject"] = "Verify your email"
    msg["From"] = "no-reply@greenbasket.com"
    msg["To"] = email

    # sends the mail
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        resp = smtp.login(user=SMTP_USER, password=SMTP_PASSWORD)
        logger.log_debug(f"Response: {resp}")
        smtp.sendmail("olalekan.o.ogundele@gmail.com", [email], msg.as_string())
        return True


def authenticate_user(username: str, password: str) -> models.User | None:
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
    """Registers a new user"""
    with UnitOfWork() as uow:
        try:
            user_service = UserService(uow.session)
            user_email = user_data.email
            verification_code = totp.now()
            is_code_sent = send_verification_email(user_email, verification_code)
            db_user = user_service.register_user(user_data.dict())
            user = User(**db_user.dict())
            if not is_code_sent:
                return JSONResponse(
                    {"status": "error", "message": "Error sending verification code"},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return JSONResponse({"status": "success", "user": user.dict()})
        except UserAlreadyExistsException:
            return JSONResponse(
                {"status": "error", "message": "User already exists"},
                status_code=status.HTTP_409_CONFLICT,
            )
        except UserRegistrationException:
            return JSONResponse(
                {"status": "error", "message": "Error creating a user"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except smtplib.SMTPAuthenticationError:
            return JSONResponse(
                {"status": "error", "message": "Error sending verification code"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@router.post("/user/verify")
def verify_code(verfifcation_data: Annotated[UserVerification, Body()]):
    """Verifies the verification code"""
    with UnitOfWork() as uow:
        user_service = UserService(uow.session)
        verification_code = verfifcation_data.verification_code
        user_email = verfifcation_data.user_email
        if totp.verify(verification_code):
            is_verified = user_service.change_user_verification_status(user_email)
            if is_verified:
                return JSONResponse(
                    {"status": "success", "message": "User verification successful"}
                )
            else:
                return JSONResponse(
                    {"status": "error", "message": "Error verifying user"}
                )
        else:
            return JSONResponse(
                {"status": "error", "message": "Invalid verification code"}
            )


@router.get("/user/resend-verification")
def resend_verification_code(email: Annotated[str, Query()]):
    """Resends the verification code"""
    user_email = email
    verification_code = totp.now()
    is_code_sent = send_verification_email(user_email, verification_code)
    if not is_code_sent:
        return JSONResponse(
            {"status": "error", "message": "Error sending verification code"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return JSONResponse({"status": "success", "message": "Verification code sent"})


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
    db_user = authenticate_user(str(email_address), str(password))

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    logger.log_debug(f"User data: {db_user.dict()}")
    user = User(**db_user.dict())
    response = LoginResponse(status="success", access_token=access_token, user=user)
    return JSONResponse(
        response.dict(),
        status_code=status.HTTP_200_OK,
    )
