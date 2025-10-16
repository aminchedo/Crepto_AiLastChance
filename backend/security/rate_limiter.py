from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit decorators
def rate_limit(limit: str):
    """Rate limit decorator for endpoints."""
    return limiter.limit(limit)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded: {exc.detail}"
    )

# Common rate limits
MARKET_DATA_LIMIT = "100/minute"
AUTH_LIMIT = "10/minute"
GENERAL_LIMIT = "200/minute"