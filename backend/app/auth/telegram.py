import hashlib
import hmac
import json
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, unquote


def parse_and_validate_init_data(
    init_data_raw: str,
    bot_token: str,
    allow_dev_fallback: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Validate Telegram Mini App initData according to Telegram's cryptographic specification.
    Returns parsed user dict or None if invalid.
    """
    if not init_data_raw:
        return None

    # Development convenience: if in dev mode and mock header provided
    if allow_dev_fallback and init_data_raw.startswith("dev_"):
        parts = init_data_raw.split("_")
        user_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 123456789
        return {
            "id": user_id,
            "first_name": "Developer",
            "username": "developer",
            "is_dev": True,
        }

    try:
        parsed_data = dict(parse_qsl(init_data_raw, keep_blank_values=True))
        received_hash = parsed_data.pop("hash", None)

        if not received_hash or not bot_token:
            # If no bot token provided and dev mode is active, allow for local testing
            if allow_dev_fallback and "user" in parsed_data:
                return json.loads(unquote(parsed_data["user"]))
            return None

        # Build data-check-string: key=value sorted alphabetically joined by newline
        data_check_list = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = "\n".join(data_check_list)

        # secret_key = HMAC_SHA256("WebAppData", bot_token)
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        # calculated_hash = HMAC_SHA256(secret_key, data_check_string)
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(calculated_hash, received_hash):
            user_data = parsed_data.get("user")
            if user_data:
                return json.loads(unquote(user_data))
            return parsed_data
        return None
    except Exception:
        return None

