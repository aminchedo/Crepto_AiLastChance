from datetime import datetime, timedelta
from typing import List, Optional

from api.deps import get_current_admin_user
from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
try:
    from ml.model import crypto_model
except ImportError:
    crypto_model = None
from models.alert import Alert, AlertHistory
from models.model_metrics import ModelMetrics
from models.user import User
from monitoring.metrics import (AI_PREDICTION_COUNT, AI_TRAINING_EPOCHS,
                                DB_QUERY_COUNT, IN_PROGRESS_REQUESTS,
                                REDIS_HIT_COUNT, REDIS_MISS_COUNT,
                                REQUEST_COUNT, REQUEST_LATENCY)
from schemas.admin import (ModelStatusResponse, SystemMetricsResponse,
                           UserActionRequest, UserResponse)
from services.alert_service import alert_service
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system metrics for admin dashboard."""
    try:
        # Get user statistics
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar()

        active_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()

        # Get alert statistics
        total_alerts_result = await db.execute(select(func.count(Alert.id)))
        total_alerts = total_alerts_result.scalar()

        triggered_alerts_result = await db.execute(select(func.count(AlertHistory.id)))
        triggered_alerts = triggered_alerts_result.scalar()

        # Get model metrics
        latest_metrics_result = await db.execute(
            select(ModelMetrics).order_by(ModelMetrics.timestamp.desc()).limit(1)
        )
        latest_metrics = latest_metrics_result.scalar_one_or_none()

        # Get Prometheus metrics
        metrics_data = {
            "api_requests": (
                REQUEST_COUNT._value.get() if hasattr(REQUEST_COUNT, "_value") else 0
            ),
            "avg_response_time": (
                REQUEST_LATENCY._sum.get() / max(REQUEST_LATENCY._count.get(), 1)
                if hasattr(REQUEST_LATENCY, "_sum")
                else 0
            ),
            "websocket_connections": 0,  # Would need to track this
            "ai_predictions": (
                AI_PREDICTION_COUNT._value.get()
                if hasattr(AI_PREDICTION_COUNT, "_value")
                else 0
            ),
            "alerts_triggered": triggered_alerts,
            "database_queries": (
                DB_QUERY_COUNT._value.get() if hasattr(DB_QUERY_COUNT, "_value") else 0
            ),
            "redis_hits": (
                REDIS_HIT_COUNT._value.get()
                if hasattr(REDIS_HIT_COUNT, "_value")
                else 0
            ),
            "redis_misses": (
                REDIS_MISS_COUNT._value.get()
                if hasattr(REDIS_MISS_COUNT, "_value")
                else 0
            ),
            "error_rate": 0.0,  # Would need to track errors
            "memory_usage": 0.0,  # Would need system monitoring
            "cpu_usage": 0.0,  # Would need system monitoring
        }

        return SystemMetricsResponse(
            active_users=active_users, total_users=total_users, **metrics_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all users for admin management."""
    try:
        result = await db.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()

        return [UserResponse.from_orm(user) for user in users]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle user active status."""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prevent admin from deactivating themselves
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

        user.is_active = not user.is_active
        await db.commit()

        return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user."""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prevent admin from deleting themselves
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")

        await db.delete(user)
        await db.commit()

        return {"message": "User deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-status", response_model=ModelStatusResponse)
async def get_model_status(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI model status and metrics."""
    try:
        # Get latest model metrics
        result = await db.execute(
            select(ModelMetrics).order_by(ModelMetrics.timestamp.desc()).limit(1)
        )
        latest_metrics = result.scalar_one_or_none()

        # Check if model is loaded
        model_loaded = crypto_model.model is not None

        return ModelStatusResponse(
            model_name="crypto_lstm",
            accuracy=latest_metrics.accuracy if latest_metrics else 0.0,
            loss=latest_metrics.loss if latest_metrics else 0.0,
            last_trained=latest_metrics.timestamp if latest_metrics else None,
            training_status="loaded" if model_loaded else "not_loaded",
            is_training=False,  # Would need to track training status
            total_predictions=(
                AI_PREDICTION_COUNT._value.get()
                if hasattr(AI_PREDICTION_COUNT, "_value")
                else 0
            ),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/model/retrain")
async def retrain_model(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Start model retraining."""
    try:
        from ml.trainer import model_trainer

        # Start training in background
        await model_trainer.start_training()

        return {"message": "Model retraining started"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/model/stop-training")
async def stop_model_training(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Stop model training."""
    try:
        from ml.trainer import model_trainer

        await model_trainer.stop_training()

        return {"message": "Model training stopped"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/clear-cache")
async def clear_cache(current_user: User = Depends(get_current_admin_user)):
    """Clear Redis cache."""
    try:
        from db.redis_client import redis_client

        # Clear all cache keys
        await redis_client.delete("*")

        return {"message": "Cache cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/system/restart-services")
async def restart_services(current_user: User = Depends(get_current_admin_user)):
    """Restart system services."""
    try:
        # This would typically involve system commands
        # For now, just restart the alert service
        await alert_service.stop_alert_monitoring()
        await alert_service.start_alert_monitoring()

        return {"message": "Services restarted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_system_logs(
    lines: int = Query(100, description="Number of log lines to return"),
    current_user: User = Depends(get_current_admin_user),
):
    """Get system logs."""
    try:
        # This would read from log files
        # For now, return placeholder
        return {
            "logs": [
                f"Log entry {i}: System running normally"
                for i in range(1, min(lines, 50) + 1)
            ],
            "total_lines": 50,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
