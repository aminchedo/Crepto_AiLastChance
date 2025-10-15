from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from models.user import User, UserRole
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT token."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Create a new user."""
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user."""
        user = await AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        return user

    @staticmethod
    async def update_password(db: AsyncSession, user: User, new_password: str) -> User:
        """Update user password."""
        user.hashed_password = AuthService.get_password_hash(new_password)
        await db.commit()
        await db.refresh(user)
        return user
