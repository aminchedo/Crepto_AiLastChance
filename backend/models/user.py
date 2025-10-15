import enum

from db.database import Base
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Telegram integration
    telegram_chat_id = Column(String, nullable=True)
    telegram_enabled = Column(Boolean, default=False, nullable=False)

    # Email notifications
    email_enabled = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    portfolios = relationship(
        "Portfolio", back_populates="user", cascade="all, delete-orphan"
    )
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
