from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SystemMetricsResponse(BaseModel):
    active_users: int
    total_users: int
    api_requests: int
    websocket_connections: int
    ai_predictions: int
    alerts_triggered: int
    database_queries: int
    redis_hits: int
    redis_misses: int
    error_rate: float
    avg_response_time: float
    memory_usage: float
    cpu_usage: float


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool
    is_admin: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class ModelStatusResponse(BaseModel):
    model_name: str
    accuracy: float
    loss: float
    last_trained: Optional[datetime]
    training_status: str
    is_training: bool
    total_predictions: int


class UserActionRequest(BaseModel):
    action: str
    reason: Optional[str] = None
