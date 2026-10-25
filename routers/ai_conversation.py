from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
import asyncpg

from database.database import get_db, get_authenticated_db
from schemas.ai import (
    ConversationCreateSchema,
    ConversationResponseSchema,
    MessageCreateSchema,
    MessageResponseSchema,
)
from services import ai_conversation as conversation_service
from core.dependency import get_current_user

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    data: ConversationCreateSchema,
    user_id: int = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_authenticated_db),
):
    return await conversation_service.create_conversation(
        user_id=user_id,
        title=data.title,
        db=db,
    )


@router.get(
    "",
    response_model=list[ConversationResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_conversations(
    user_id: int = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_authenticated_db),
):
    return await conversation_service.get_conversations(
        user_id=user_id,
        db=db,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_conversation(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_authenticated_db),
):
    deleted = await conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return {"message": "Conversation deleted successfully"}


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def get_messages(
    conversation_id: int,
    user_id: int = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_authenticated_db),
):
    messages = await conversation_service.get_messages(
        conversation_id=conversation_id,
        user_id=user_id,
        db=db,
    )

    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return messages


@router.post(
    "/{conversation_id}/messages",
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: int,
    data: MessageCreateSchema,
    user_id: int = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_authenticated_db),
):
    message = await conversation_service.create_message(
        conversation_id=conversation_id,
        user_id=user_id,
        content=data.content,
        db=db,
    )

    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return StreamingResponse(
        message,
        media_type="text/event-stream",
        status_code=status.HTTP_201_CREATED,
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )