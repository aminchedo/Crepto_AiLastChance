import enum

from db.database import Base
from sqlalchemy import (JSON, Column, DateTime, Enum, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AuditAction(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    PORTFOLIO_CREATE = "portfolio_create"
    PORTFOLIO_UPDATE = "portfolio_update"
    PORTFOLIO_DELETE = "portfolio_delete"
    POSITION_ADD = "position_add"
    POSITION_UPDATE = "position_update"
    POSITION_DELETE = "position_delete"
    ALERT_CREATE = "alert_create"
    ALERT_UPDATE = "alert_update"
    ALERT_DELETE = "alert_delete"
    SETTINGS_UPDATE = "settings_update"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)

    # Request details
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Change details
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    # Additional metadata
    extra_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
