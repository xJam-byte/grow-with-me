from typing import List, Optional
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.repositories.note import NoteRepository
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NoteRepository(db)

    async def list_notes(
        self,
        user_id: int,
        category: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[NoteResponse]:
        notes = await self.repo.get_user_notes(
            user_id=user_id,
            category=category,
            is_favorite=is_favorite,
            limit=limit,
            offset=offset,
        )
        return [NoteResponse.model_validate(n) for n in notes]

    async def get_note(self, user_id: int, note_id: int) -> Optional[NoteResponse]:
        note = await self.repo.get_user_note(note_id, user_id)
        if not note:
            return None
        return NoteResponse.model_validate(note)

    async def create_note(self, user_id: int, payload: NoteCreate) -> NoteResponse:
        note = Note(
            user_id=user_id,
            title=payload.title,
            content=payload.content,
            category=payload.category,
            tags=payload.tags or [],
            is_favorite=payload.is_favorite,
        )
        saved = await self.repo.add(note)
        return NoteResponse.model_validate(saved)

    async def update_note(
        self, user_id: int, note_id: int, payload: NoteUpdate
    ) -> Optional[NoteResponse]:
        note = await self.repo.get_user_note(note_id, user_id)
        if not note:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(note, field, value)

        await self.db.flush()
        await self.db.refresh(note)
        return NoteResponse.model_validate(note)

    async def delete_note(self, user_id: int, note_id: int) -> bool:
        note = await self.repo.get_user_note(note_id, user_id)
        if not note:
            return False
        await self.db.execute(delete(Note).where(Note.id == note_id))
        await self.db.flush()
        return True

    async def search_notes(self, user_id: int, query: str) -> List[NoteResponse]:
        notes = await self.repo.search_notes(user_id=user_id, query=query)
        return [NoteResponse.model_validate(n) for n in notes]

    async def toggle_favorite(self, user_id: int, note_id: int) -> bool:
        return await self.repo.toggle_favorite(note_id, user_id)
