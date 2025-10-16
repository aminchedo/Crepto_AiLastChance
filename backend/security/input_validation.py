from pydantic import BaseModel, validator
import re
from typing import Optional

class MarketRequest(BaseModel):
    symbol: str
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z]{1,10}$', v):
            raise ValueError('Invalid symbol format. Must be 1-10 uppercase letters.')
        return v.upper()

class TimeRangeRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period: str = "1h"
    
    @validator('period')
    def validate_period(cls, v):
        allowed_periods = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
        if v not in allowed_periods:
            raise ValueError(f'Invalid period. Must be one of: {", ".join(allowed_periods)}')
        return v

class PaginationRequest(BaseModel):
    page: int = 1
    limit: int = 20
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be greater than 0')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v