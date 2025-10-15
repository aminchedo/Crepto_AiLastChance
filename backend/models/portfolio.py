import enum

from db.database import Base
from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, default="Default Portfolio")
    description = Column(String, nullable=True)
    is_default = Column(Integer, default=1, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship(
        "Position", back_populates="portfolio", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Portfolio(id={self.id}, user_id={self.user_id}, name={self.name})>"


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    transactions = relationship(
        "Transaction", back_populates="position", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Position(id={self.id}, symbol={self.symbol}, quantity={self.quantity})>"
        )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0, nullable=False)
    notes = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    position = relationship("Position", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, quantity={self.quantity})>"
