"""Exception related to user's service"""

class UserAlreadyExistsException(Exception):
    """User already exists"""

class UserNotFoundException(Exception):
    """User not found"""

class UserRegistrationException(Exception):
    """User registration failed"""
