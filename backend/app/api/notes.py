from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.note import NoteService

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("", response_model=List[NoteResponse])
async def list_notes(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorite notes"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notes with optional category and favorite filtering."""
    service = NoteService(db)
    return await service.list_notes(
        user_id=current_user.id,
        category=category,
        is_favorite=is_favorite,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new note (quick thought, idea, quote, book note, goal)."""
    service = NoteService(db)
    return await service.create_note(current_user.id, payload)


@router.get("/search", response_model=List[NoteResponse])
async def search_notes(
    q: str = Query(..., min_length=1, description="Search query string"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search notes by title and content."""
    service = NoteService(db)
    return await service.search_notes(current_user.id, q)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note_detail(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single note details."""
    service = NoteService(db)
    note = await service.get_note(current_user.id, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update note content, title, tags, or category."""
    service = NoteService(db)
    updated = await service.update_note(current_user.id, note_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a note."""
    service = NoteService(db)
    success = await service.delete_note(current_user.id, note_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@router.post("/{note_id}/favorite")
async def toggle_note_favorite(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle favorite star on a note."""
    service = NoteService(db)
    try:
        is_favorite = await service.toggle_favorite(current_user.id, note_id)
        return {"id": note_id, "is_favorite": is_favorite}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
