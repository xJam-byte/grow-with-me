from datetime import date
import pytest

from app.ai.coach_service import AICoachService
from app.ai.tools import execute_ai_tool
from app.repositories.user import UserRepository
from app.services.seed import seed_user_defaults


@pytest.mark.asyncio
async def test_ai_coach_chat_and_history(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=987654321, username="ai_test_user")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    service = AICoachService(db_session)
    await service.clear_history(user.id)

    # 1. Send chat message to coach
    response = await service.chat(user, "Как у меня дела сегодня?")
    assert response.role == "assistant"
    assert len(response.message) > 10
    assert "привыч" in response.message.lower()

    # 2. Check history
    history = await service.get_history(user.id)
    assert len(history) >= 2  # user message + assistant message
    assert history[0].role == "user"
    assert history[1].role == "assistant"

    # 3. Clear history
    await service.clear_history(user.id)
    empty_history = await service.get_history(user.id)
    assert len(empty_history) == 0


@pytest.mark.asyncio
async def test_ai_tools_execution(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=123987456, username="tools_test_user")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    # 1. Execute get_user_profile tool
    profile_json = await execute_ai_tool("get_user_profile", {}, user.id, user, db_session)
    assert "principles" in profile_json

    # 2. Execute get_habits_today
    habits_json = await execute_ai_tool("get_habits_today", {}, user.id, user, db_session)
    assert "habits" in habits_json

    # 3. Execute get_habits_stats
    stats_json = await execute_ai_tool("get_habits_stats", {}, user.id, user, db_session)
    assert "total_habits" in stats_json


@pytest.mark.asyncio
async def test_ai_weekly_analysis_and_usage(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=777888999, username="analysis_test_user")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    service = AICoachService(db_session)

    # 1. Weekly analysis
    analysis = await service.analyze_week(user)
    assert analysis.overall_score >= 1.0
    assert len(analysis.strengths) > 0
    assert len(analysis.weaknesses) > 0
    assert len(analysis.action_plan) > 0

    # 2. Token usage reporting
    usage = await service.get_token_usage_stats(user)
    assert usage.daily_limit >= 1000
    assert usage.estimated_cost_usd >= 0.0
