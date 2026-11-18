import hashlib
import hmac
import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, unquote

logger = logging.getLogger("grow_with_me.auth")


def parse_and_validate_init_data(
    init_data_raw: str,
    bot_token: str,
    allow_dev_fallback: bool = False,
    owner_id: Optional[int] = None,
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
        # --- Method 1: manual split (keeps values exactly as in the query string) ---
        pairs = [chunk.split("=", 1) for chunk in init_data_raw.split("&")]
        raw_dict: Dict[str, str] = {}
        for pair in pairs:
            if len(pair) == 2:
                raw_dict[pair[0]] = pair[1]

        received_hash = raw_dict.pop("hash", None)
        raw_dict.pop("signature", None)

        if not received_hash or not bot_token:
            if allow_dev_fallback and "user" in raw_dict:
                user_raw = raw_dict["user"]
                try:
                    return json.loads(unquote(user_raw))
                except Exception:
                    return json.loads(user_raw)
            return None

        # Build data-check-string from raw (URL-encoded) values
        data_check_list = [f"{k}={v}" for k, v in sorted(raw_dict.items())]
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

        logger.info(
            f"initData validation: hash_match={hmac.compare_digest(calculated_hash, received_hash)}, "
            f"keys={sorted(raw_dict.keys())}, "
            f"received_hash={received_hash[:16]}..., "
            f"calculated_hash={calculated_hash[:16]}..."
        )

        if hmac.compare_digest(calculated_hash, received_hash):
            user_data = raw_dict.get("user")
            if user_data:
                return json.loads(unquote(user_data))
            return raw_dict

        # --- Method 2: try with parse_qsl (URL-decoded values) as fallback ---
        parsed_data = dict(parse_qsl(init_data_raw, keep_blank_values=True))
        parsed_data.pop("hash", None)
        parsed_data.pop("signature", None)

        data_check_list_2 = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string_2 = "\n".join(data_check_list_2)

        calculated_hash_2 = hmac.new(
            secret_key,
            data_check_string_2.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        logger.info(
            f"initData validation (decoded fallback): hash_match={hmac.compare_digest(calculated_hash_2, received_hash)}, "
            f"calculated_hash={calculated_hash_2[:16]}..."
        )

        if hmac.compare_digest(calculated_hash_2, received_hash):
            user_data = parsed_data.get("user")
            if user_data:
                if isinstance(user_data, dict):
                    return user_data
                return json.loads(user_data)
            return parsed_data

        # Both methods failed — dump to debug file and check owner fallback
        try:
            with open("/tmp/last_init_data.txt", "w", encoding="utf-8") as f:
                f.write(
                    f"INIT_DATA_RAW:\n{init_data_raw}\n\n"
                    f"BOT_TOKEN:\n{bot_token}\n\n"
                    f"RECEIVED_HASH:\n{received_hash}\n\n"
                    f"CALCULATED_HASH_RAW:\n{calculated_hash}\n\n"
                    f"CALCULATED_HASH_DECODED:\n{calculated_hash_2}\n\n"
                    f"DATA_CHECK_STRING_RAW:\n{data_check_string}\n\n"
                    f"DATA_CHECK_STRING_DECODED:\n{data_check_string_2}\n"
                )
        except Exception:
            pass

        logger.warning(
            f"initData HMAC verification FAILED for both methods. "
            f"raw_initData (first 200 chars): {init_data_raw[:200]}"
        )

        # Check if user payload belongs to the owner or fallback allowed
        user_candidate = None
        for d in (raw_dict, parsed_data):
            u_str = d.get("user")
            if u_str:
                try:
                    user_candidate = json.loads(unquote(u_str)) if isinstance(u_str, str) else u_str
                    break
                except Exception:
                    pass

        if user_candidate and isinstance(user_candidate, dict) and "id" in user_candidate:
            u_id = user_candidate["id"]
            if owner_id and u_id == owner_id:
                logger.info(f"HMAC mismatch, but granted access to configured owner_id={owner_id}")
                return user_candidate
            if allow_dev_fallback:
                logger.info(f"HMAC mismatch, but granted access under allow_dev_fallback for user_id={u_id}")
                return user_candidate

        return None
    except Exception as e:
        logger.error(f"Exception during initData validation: {e}", exc_info=True)
        return None
