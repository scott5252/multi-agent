from __future__ import annotations

import hmac
import json
from hashlib import sha256
from urllib.parse import urlparse

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ErrorCategory


def validate_callback_url(url: str, *, allow_local_http: bool) -> None:
    parsed = urlparse(url)
    if parsed.scheme == "https":
        return
    if (
        allow_local_http
        and parsed.scheme == "http"
        and parsed.hostname
        in {
            "127.0.0.1",
            "localhost",
            "::1",
        }
    ):
        return
    raise ChannelError(
        ErrorCategory.CALLBACK_DELIVERY_FAILED,
        "Callback URL must use HTTPS outside local development.",
    )


def sign_callback_payload(payload: dict[str, object], secret: str) -> str:
    encoded = json.dumps(payload, default=str, sort_keys=True).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), encoded, sha256).hexdigest()
