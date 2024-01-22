"""Unit of Work Module"""

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils import GBLogger

logger = GBLogger("UnitOfWork")
env_vars = dotenv_values('.env')

class UnitOfWork:
    """Basic unit of work to help with database interactions"""

    def __init__(self):
        """Unit of Work Constructor"""
        self.session = None
        self.database_url = env_vars.get('DEV_DATABASE_URL')
        self.session_maker = sessionmaker(
            bind=create_engine(self.database_url)
        )
        logger.log_debug("Session maker: %s" % self.session_maker)

    def __enter__(self):
        """
        Enters the context of the object.

        Return:
            self: The object itself.
        """
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        """
        Exits the context manager and performs any necessary cleanup.
        
        :param exc_type: The type of exception being raised, if any.
        :param exc_val: The value of the exception being raised, if any.
        :param traceback: The traceback of the exception being raised, if any.
        """
        if exc_type is not None:
            self.rollback()
            self.session.close()

    def commit(self):
        """Commit the changes"""
        self.session.commit()

    def rollback(self):
        """Rollback the changes"""
        self.session.rollback()
