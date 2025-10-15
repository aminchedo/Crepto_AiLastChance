"""
Prometheus Metrics for Crepto AI Backend

This module provides Prometheus metrics collection for the FastAPI backend.
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, REGISTRY
from prometheus_client.multiprocess import MultiProcessCollector
from fastapi import Request
from fastapi.responses import Response
import time
from functools import wraps
from typing import Callable

# ===== METRICS DEFINITIONS =====

# HTTP Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# API metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint', 'method']
)

# External API metrics
external_api_requests_total = Counter(
    'external_api_requests_total',
    'Total external API requests',
    ['api_name', 'status']
)

external_api_failures_total = Counter(
    'external_api_failures_total',
    'Total external API failures',
    ['api_name', 'error_type']
)

# Database metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

database_connections_max = Gauge(
    'database_connections_max',
    'Maximum database connections allowed'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# WebSocket metrics
websocket_connections = Gauge(
    'websocket_connections',
    'Number of active WebSocket connections'
)

websocket_messages_sent_total = Counter(
    'websocket_messages_sent_total',
    'Total WebSocket messages sent'
)

websocket_messages_received_total = Counter(
    'websocket_messages_received_total',
    'Total WebSocket messages received'
)

# Application info
app_info = Info(
    'crepto_ai_backend',
    'Crepto AI Backend application info'
)

# Business metrics
user_actions_total = Counter(
    'user_actions_total',
    'Total user actions',
    ['action_type']
)

crypto_price_updates_total = Counter(
    'crypto_price_updates_total',
    'Total cryptocurrency price updates',
    ['symbol']
)

# ===== MIDDLEWARE =====

async def metrics_middleware(request: Request, call_next: Callable):
    """
    Middleware to track HTTP request metrics
    """
    method = request.method
    path = request.url.path
    
    # Start timer
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Track metrics
    http_requests_total.labels(
        method=method,
        endpoint=path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        endpoint=path
    ).observe(duration)
    
    return response

# ===== HELPER FUNCTIONS =====

def track_external_api_call(api_name: str):
    """
    Decorator to track external API calls
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                external_api_requests_total.labels(
                    api_name=api_name,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                external_api_requests_total.labels(
                    api_name=api_name,
                    status='error'
                ).inc()
                external_api_failures_total.labels(
                    api_name=api_name,
                    error_type=type(e).__name__
                ).inc()
                raise
        return wrapper
    return decorator

def track_database_query(query_type: str):
    """
    Decorator to track database queries
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                database_query_duration_seconds.labels(
                    query_type=query_type
                ).observe(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                database_query_duration_seconds.labels(
                    query_type=query_type
                ).observe(duration)
                raise
        return wrapper
    return decorator

def track_cache_access(cache_type: str, hit: bool):
    """
    Track cache hit/miss
    """
    if hit:
        cache_hits_total.labels(cache_type=cache_type).inc()
    else:
        cache_misses_total.labels(cache_type=cache_type).inc()

def set_app_info(version: str, environment: str):
    """
    Set application info metrics
    """
    app_info.info({
        'version': version,
        'environment': environment,
        'service': 'crepto-ai-backend'
    })

# ===== METRICS ENDPOINT =====

def metrics_endpoint() -> Response:
    """
    Endpoint to expose Prometheus metrics
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type='text/plain; version=0.0.4; charset=utf-8'
    )

# ===== EXAMPLE USAGE =====

# In main.py:
# from metrics import metrics_middleware, metrics_endpoint
# app.middleware("http")(metrics_middleware)
# app.add_route("/metrics", metrics_endpoint, methods=["GET"])
