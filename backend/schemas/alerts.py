from datetime import datetime
from typing import Any, Dict, List, Optional

from models.alert import AlertChannel, AlertStatus, AlertType
from pydantic import BaseModel


class AlertCreate(BaseModel):
    symbol: str
    alert_type: AlertType
    threshold_value: Optional[float] = None
    channels: List[AlertChannel] = [AlertChannel.WEBSOCKET]
    message: Optional[str] = None
    expires_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    threshold_value: Optional[float] = None
    channels: Optional[List[AlertChannel]] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    status: Optional[AlertStatus] = None


class AlertResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    alert_type: AlertType
    status: AlertStatus
    threshold_value: Optional[float]
    channels: List[AlertChannel]
    message: Optional[str]
    custom_message: Optional[str]
    trigger_count: int
    last_triggered_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    id: int
    alert_id: int
    triggered_value: Optional[float]
    message: str
    channels_sent: List[AlertChannel]
    delivery_status: Dict[str, str]
    triggered_at: datetime

    class Config:
        from_attributes = True


class AlertSummaryResponse(BaseModel):
    total_alerts: int
    active_alerts: int
    triggered_alerts: int
    expired_alerts: int
    disabled_alerts: int
    total_triggers: int
    recent_triggers: int
