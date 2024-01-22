"""Module for routing user related endpoints"""

from typing import Annotated
from fastapi import APIRouter, Body
from app.db_schema.user import UserInput, User
from app.dependencies import UnitOfWork
from app.exceptions.users import UserAlreadyExistsException, UserRegistrationException
from app.utils import GBLogger
from app.services.user_service import UserService

router = APIRouter(prefix='/users')
logger = GBLogger("UserRouter")

@router.get('/')
def get_users() -> dict:
    """Get all users"""
    with UnitOfWork() as uow:
        logger.log_debug(f"UOW's session {dir(uow.session)}")
        user_service = UserService(uow.session)
        users = user_service.get_all_users()
        return {"users": users}

@router.post('/')
def register_user(user_data: Annotated[UserInput, Body()]) -> dict:
    """Register a new user"""
    with UnitOfWork() as uow:
        try:
                
            logger.log_debug(f"User Data: {user_data}")
            user_service = UserService(uow.session)
            db_user = user_service.register_user(user_data)
            user = User(**db_user.dict())
            return {"status": "success", "user": user.dict()}
        except UserAlreadyExistsException:
            return {"status": "error", "message": "User already exists"}
        except UserRegistrationException as e:
            logger.log_error(f"Error creating a user: {e}")
            return {"status": "error", "message": "Error creating a user"}
    