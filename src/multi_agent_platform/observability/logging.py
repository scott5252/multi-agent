from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

REDACTED = "***REDACTED***"
SECRET_KEYS = ("secret", "token", "password", "api_key", "authorization")


def redact_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if any(marker in key.lower() for marker in SECRET_KEYS):
            redacted[key] = REDACTED
        elif isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra") and isinstance(record.extra, Mapping):
            payload.update(redact_mapping(record.extra))
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("multi_agent_platform")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger
