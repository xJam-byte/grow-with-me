from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.allah_names import ALLAH_NAMES_DATA
from app.models.allah_name import AllahName


async def seed_allah_names(db: AsyncSession) -> None:
    """Populates the allah_names table with authentic 99 names if empty."""
    count_res = await db.execute(select(func.count(AllahName.id)))
    count = count_res.scalar() or 0

    if count == 0:
        for item in ALLAH_NAMES_DATA:
            name_obj = AllahName(
                number=item["number"],
                arabic_name=item["arabic_name"],
                transliteration=item["transliteration"],
                meaning_ru=item["meaning_ru"],
                explanation=item["explanation"],
                life_reflection=item["life_reflection"],
                source_reference=item.get("source_reference"),
            )
            db.add(name_obj)
        await db.flush()
