from app.auth.telegram import parse_and_validate_init_data


def test_telegram_auth_dev_fallback():
    # Dev mock string
    result = parse_and_validate_init_data("dev_987654", bot_token="", allow_dev_fallback=True)
    assert result is not None
    assert result["id"] == 987654
    assert result["is_dev"] is True


def test_telegram_auth_empty():
    result = parse_and_validate_init_data("", bot_token="token")
    assert result is None
