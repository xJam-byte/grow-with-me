from datetime import date
import pytest

from app.repositories.user import UserRepository
from app.schemas.progress import WeeklyAssessmentCreate
from app.services.habit import HabitService
from app.services.progress import ProgressService
from app.services.seed import seed_user_defaults


@pytest.mark.asyncio
async def test_progress_dashboard_and_areas(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=333222111, username="progress_user")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    # Toggle one habit
    habit_service = HabitService(db_session)
    habits = await habit_service.get_today_habits(user.id, date.today())
    assert len(habits) > 0
    await habit_service.toggle_habit(user.id, habits[0].id, date.today())

    # Get Dashboard
    progress_service = ProgressService(db_session)
    dash = await progress_service.get_dashboard(user.id)
    assert dash.today_completed == 1
    assert dash.today_total == 10
    assert dash.today_completion_rate == 10.0
    assert len(dash.weekly_chart) == 7
    assert len(dash.monthly_heatmap) == 30
    assert len(dash.streaks) == 10

    # Get Areas Progress
    areas = await progress_service.get_areas_progress(user.id)
    assert len(areas) == 5
    area_slugs = {a.slug for a in areas}
    assert "spirituality" in area_slugs
    assert "intellectual" in area_slugs
    assert "physical" in area_slugs
    assert "mental" in area_slugs
    assert "academic" in area_slugs


@pytest.mark.asyncio
async def test_weekly_assessment_and_ai_report(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_or_create(telegram_id=999111222, username="assessment_user")
    await seed_user_defaults(user.id, db_session)
    await db_session.commit()

    progress_service = ProgressService(db_session)

    # 1. Save Weekly Assessment
    payload = WeeklyAssessmentCreate(
        score_spirituality=5,
        score_intellectual=4,
        score_physical=3,
        score_mental=4,
        score_academic=3,
        went_well="Качественно читал каждый день и держал ранний подъём.",
        went_wrong="Пропустил одну тренировку в четверг.",
        difficulties="Усталость к концу рабочей недели.",
        achievements="Завершил 6 тем из Daily Knowledge.",
        learned="Нельзя откладывать спорт на поздний вечер.",
        next_week_priorities="Закрыть все 4 тренировки без пропусков.",
    )
    assessment = await progress_service.save_assessment(user.id, payload)
    assert assessment.id is not None
    assert assessment.score_spirituality == 5
    assert assessment.score_physical == 3

    # 2. Generate Weekly AI Report
    updated = await progress_service.generate_ai_report(user.id, assessment.id)
    assert updated.ai_report is not None
    assert "overall_evaluation" in updated.ai_report
    assert "strongest_area" in updated.ai_report
    assert "focus_area" in updated.ai_report
    assert len(updated.ai_report["recommendations"]) > 0

    # 3. Retrieve Latest
    latest = await progress_service.get_latest_assessment(user.id)
    assert latest is not None
    assert latest.id == assessment.id
    assert latest.ai_report is not None

    # 4. Retrieve History
    history = await progress_service.get_assessment_history(user.id, limit=5)
    assert len(history) >= 1
