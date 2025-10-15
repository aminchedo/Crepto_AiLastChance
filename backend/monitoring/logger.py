"""
Structured logging system for BOLT AI Neural Agent System
"""

import json
import logging
import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory


class StructuredLogger:
    """Structured logger with correlation IDs and context management"""

    def __init__(self, name: str = "bolt-ai", log_level: str = "INFO"):
        self.name = name
        self.log_level = log_level
        self.logger = None
        self.context = {}
        self.setup_logging()

    def setup_logging(self):
        """Setup structured logging configuration"""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Setup file handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / f"{self.name}-{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(getattr(logging, self.log_level))

        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))

        # Setup formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        # Get structured logger
        self.logger = structlog.get_logger(self.name)

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID"""
        return str(uuid.uuid4())

    def add_context(self, **kwargs):
        """Add context to logger"""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear logger context"""
        self.context.clear()

    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(message, **self.context, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(message, **self.context, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(message, **self.context, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(message, **self.context, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self.logger.critical(message, **self.context, **kwargs)

    def log_training_start(self, trainer_id: str, config: Dict[str, Any]):
        """Log training start event"""
        self.add_context(
            trainer_id=trainer_id, event_type="training_start", config=config
        )
        self.info("Training started", trainer_id=trainer_id)

    def log_training_epoch(
        self, trainer_id: str, epoch: int, metrics: Dict[str, float]
    ):
        """Log training epoch event"""
        self.add_context(
            trainer_id=trainer_id,
            event_type="training_epoch",
            epoch=epoch,
            metrics=metrics,
        )
        self.info(f"Epoch {epoch} completed", metrics=metrics)

    def log_training_end(self, trainer_id: str, final_metrics: Dict[str, float]):
        """Log training end event"""
        self.add_context(
            trainer_id=trainer_id,
            event_type="training_end",
            final_metrics=final_metrics,
        )
        self.info("Training completed", final_metrics=final_metrics)

    def log_prediction(
        self, prediction_id: str, symbol: str, prediction: Dict[str, float]
    ):
        """Log prediction event"""
        self.add_context(
            prediction_id=prediction_id,
            event_type="prediction",
            symbol=symbol,
            prediction=prediction,
        )
        self.info(f"Prediction generated for {symbol}", prediction=prediction)

    def log_instability_event(self, trainer_id: str, reason: str, recovery_action: str):
        """Log instability detection event"""
        self.add_context(
            trainer_id=trainer_id,
            event_type="instability_detected",
            reason=reason,
            recovery_action=recovery_action,
        )
        self.warning(f"Instability detected: {reason}", recovery_action=recovery_action)

    def log_api_request(
        self,
        request_id: str,
        method: str,
        endpoint: str,
        status_code: int,
        duration_ms: float,
    ):
        """Log API request event"""
        self.add_context(
            request_id=request_id,
            event_type="api_request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
        )
        self.info(
            f"API request: {method} {endpoint}",
            status_code=status_code,
            duration_ms=duration_ms,
        )

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log error with full context"""
        error_context = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }

        if context:
            error_context.update(context)

        self.add_context(**error_context)
        self.error(f"Error occurred: {error}", **error_context)

    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        tags: Dict[str, str] = None,
    ):
        """Log performance metric"""
        metric_context = {
            "event_type": "performance_metric",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
        }

        if tags:
            metric_context["tags"] = tags

        self.add_context(**metric_context)
        self.info(
            f"Performance metric: {metric_name}", value=value, unit=unit, tags=tags
        )


# Global logger instance
logger = StructuredLogger()


def get_logger(name: str = None) -> StructuredLogger:
    """Get logger instance"""
    if name:
        return StructuredLogger(name)
    return logger


# Context manager for correlation IDs
class LogContext:
    """Context manager for structured logging"""

    def __init__(self, correlation_id: str = None, **context):
        self.correlation_id = correlation_id or logger.generate_correlation_id()
        self.context = context
        self.original_context = {}

    def __enter__(self):
        self.original_context = logger.context.copy()
        logger.add_context(correlation_id=self.correlation_id, **self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.context = self.original_context
        if exc_type:
            logger.log_error(exc_val, {"correlation_id": self.correlation_id})


# Decorator for automatic logging
def log_function_call(func):
    """Decorator to automatically log function calls"""

    def wrapper(*args, **kwargs):
        correlation_id = logger.generate_correlation_id()
        with LogContext(correlation_id, function=func.__name__):
            logger.info(f"Function call: {func.__name__}", args=args, kwargs=kwargs)
            try:
                result = func(*args, **kwargs)
                logger.info(f"Function completed: {func.__name__}")
                return result
            except Exception as e:
                logger.log_error(e, {"function": func.__name__})
                raise

    return wrapper


# Performance monitoring decorator
def log_performance(func):
    """Decorator to log function performance"""

    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        correlation_id = logger.generate_correlation_id()

        with LogContext(correlation_id, function=func.__name__):
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.log_performance_metric(
                    f"{func.__name__}_duration", duration, "ms"
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                logger.log_performance_metric(
                    f"{func.__name__}_error_duration", duration, "ms"
                )
                logger.log_error(e, {"function": func.__name__})
                raise

    return wrapper
