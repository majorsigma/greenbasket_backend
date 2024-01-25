"""User Service Module"""
# pylint: disable=E0401

import typing

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.exceptions.users import UserAlreadyExistsException, UserRegistrationException
from app.models import User
from app.utils import GBLogger

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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

    @staticmethod
    def get_password_hash(password: str):
        """
        Returns a hashed password.
        """
        return password_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str):
        """
        Verifies a password against a hashed password.
        """
        return password_context.verify(password, hashed_password)

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
            user = self.session.query(User).filter(email == email).first()
            return user
        except Exception as e:
            raise e

    def get_user_by_username(self, username: str) -> User | None:
        """Retrieves a user by his/her username"""
        try:
            user = self.session.query(User).where(User.username == username).first()
            return user
        except Exception as e:
            raise e

    def change_user_verification_status(self, user_email: str) -> bool:
        """change the verification status of the user"""
        try:
            user = self.get_user_by_email(user_email)
            user.is_verified = True
            self.session.commit()
            return True
        except Exception as e:
            raise e

    def register_user(self, body: dict) -> User:
        """Registers a new users into the system. If the user already exists,
        return the user else raise an exception.
        """
        try:
            user = User(**body)
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
            # raise e
            # logger.log_error(f"Error creating a user: {e}")
            raise UserRegistrationException from e
