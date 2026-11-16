from typing import List, Optional
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.repositories.base import BaseRepository


class NoteRepository(BaseRepository[Note]):
    def __init__(self, db: AsyncSession):
        super().__init__(Note, db)

    async def get_user_notes(
        self,
        user_id: int,
        category: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Note]:
        stmt = (
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(desc(Note.created_at))
            .limit(limit)
            .offset(offset)
        )
        if category:
            stmt = stmt.where(Note.category == category)
        if is_favorite is not None:
            stmt = stmt.where(Note.is_favorite == is_favorite)

        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_user_note(self, note_id: int, user_id: int) -> Optional[Note]:
        stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def search_notes(self, user_id: int, query: str, limit: int = 30) -> List[Note]:
        search_pattern = f"%{query}%"
        stmt = (
            select(Note)
            .where(
                Note.user_id == user_id,
                or_(
                    Note.title.ilike(search_pattern),
                    Note.content.ilike(search_pattern),
                ),
            )
            .order_by(desc(Note.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def toggle_favorite(self, note_id: int, user_id: int) -> bool:
        note = await self.get_user_note(note_id, user_id)
        if not note:
            raise ValueError("Note not found")
        note.is_favorite = not note.is_favorite
        await self.db.flush()
        return note.is_favorite
