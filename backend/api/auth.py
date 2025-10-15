from api.deps import get_current_user
from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.audit_log import AuditAction, AuditLog
from models.user import User
from schemas.auth import (PasswordChange, Token, UserLogin, UserRegister,
                          UserResponse, UserUpdate)
from services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Check if username already exists
    existing_username = await AuthService.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Create user
    user = await AuthService.create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
    )

    # Log registration
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.REGISTER,
        resource_type="user",
        resource_id=str(user.id),
    )
    db.add(audit_log)
    await db.commit()

    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get access token."""
    user = await AuthService.authenticate_user(
        db, credentials.email, credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # Log login
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.LOGIN,
        resource_type="user",
        resource_id=str(user.id),
    )
    db.add(audit_log)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    payload = AuthService.decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await AuthService.get_user_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    new_access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    new_refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user information."""
    old_values = {
        "full_name": current_user.full_name,
        "telegram_chat_id": current_user.telegram_chat_id,
        "telegram_enabled": current_user.telegram_enabled,
        "email_enabled": current_user.email_enabled,
    }

    # Update fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.telegram_chat_id is not None:
        current_user.telegram_chat_id = user_update.telegram_chat_id
    if user_update.telegram_enabled is not None:
        current_user.telegram_enabled = user_update.telegram_enabled
    if user_update.email_enabled is not None:
        current_user.email_enabled = user_update.email_enabled

    await db.commit()
    await db.refresh(current_user)

    # Log update
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.PROFILE_UPDATE,
        resource_type="user",
        resource_id=str(current_user.id),
        old_values=old_values,
        new_values=user_update.dict(exclude_unset=True),
    )
    db.add(audit_log)
    await db.commit()

    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password."""
    # Verify old password
    if not AuthService.verify_password(
        password_data.old_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )

    # Update password
    await AuthService.update_password(db, current_user, password_data.new_password)

    # Log password change
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.PASSWORD_CHANGE,
        resource_type="user",
        resource_id=str(current_user.id),
    )
    db.add(audit_log)
    await db.commit()

    return {"message": "Password changed successfully"}
