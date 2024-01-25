"""User Model"""
#pylint: disable=E0401

from datetime import datetime
from sqlalchemy import Boolean, String, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.utils import generate_uuid

class Base(DeclarativeBase):
    """Base model class for other models"""
    naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    metadata = MetaData(naming_convention=naming_convention)

class User(Base):
    """Users table"""
    __tablename__ = "users"

    uid = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(String(255), unique=True)
    date_of_birth: Mapped[datetime] = mapped_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    address: Mapped[str] = mapped_column(String(1000), nullable=True)
    lga: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def dict(self):
        """
        Returns a dictionary representation of the user object
        """
        return {
            "uid": self.uid,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "date_of_birth": self.date_of_birth.isoformat(),
            "is_active": self.is_active,
            "is_2fa_enabled": self.is_2fa_enabled,
            "is_online": self.is_online,
            "is_verified": self.is_verified,
            "address": self.address,
            "lga": self.lga,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
