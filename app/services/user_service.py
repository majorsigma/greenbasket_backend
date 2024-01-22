"""User Service Module"""

import typing

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User
from app.exceptions.users import UserAlreadyExistsException, UserRegistrationException
from app.utils import GBLogger

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logger = GBLogger("UserService")

class UserService:
    """User service class"""

    def __init__(self, session: Session):
        """
        Creates an instance of UserService class.

        Args:
            session: The session object
        """
        self.session = session

    def get_all_users(self) -> typing.List:
        """
        Retrieves all users from the database.
        Returns a list of users.
        """
        users = []
        try:
            db_users = self.session.query(User).all()
            for user in db_users:
                users.append(user.dict())
            return users
        except Exception as exc:
            raise exc

    def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by his/her email"""
        try:
            user = self.session.query(User).get(User.email == email)
            return user
        except Exception as e:
            raise e
        
    def register_user(self, body: str) -> User:
        """Registers a new users into the system"""
        try:
            user = User(**body.dict())
            users = self.session.query(User).all()
            logger.log_debug(f"Users: {len(users)}")
            for u in users:
                if u.email == user.email:
                    raise UserAlreadyExistsException
            user.password = password_context.hash(user.password)
            self.session.add(user)
            self.session.commit()
            return user
        except UserAlreadyExistsException:
            raise
        except Exception as e:
            raise e
            # logger.log_error(f"Error creating a user: {e}")
            raise UserRegistrationException from e