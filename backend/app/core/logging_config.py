"""
Phase 23: Structured JSON Logging Configuration
Machine-readable logs for production debugging and log aggregation.
"""
import logging
import sys
import json
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Formats log records as JSON for machine-readable output."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include extra fields if any
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "strategy"):
            log_entry["strategy"] = record.strategy
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry)


def setup_logging(level: str = "INFO"):
    """Configure structured JSON logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # JSON handler for stdout
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(json_handler)

    # Quiet down noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger
