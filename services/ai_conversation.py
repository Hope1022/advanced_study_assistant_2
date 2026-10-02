import asyncpg
from ai.lang import call_llm

async def create_conversation(
    user_id: int,
    title: str | None,
    db: asyncpg.Connection,
) -> dict:

    conversation = await db.fetchrow(
        """
        INSERT INTO conversations (user_id, title)
        VALUES ($1, $2)
        RETURNING id, title, created_at
        """,
        user_id,
        title,
    )

    return dict(conversation)


async def get_conversations(
    user_id: int,
    db: asyncpg.Connection,
) -> list:

    conversations = await db.fetch(
        """
        SELECT id, title, created_at
        FROM conversations
        WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        user_id,
    )

    return [dict(c) for c in conversations]


async def delete_conversation(
    conversation_id: int,
    user_id: int,
    db: asyncpg.Connection,
) -> bool:

    result = await db.execute(
        """
        DELETE FROM conversations
        WHERE id = $1
        AND user_id = $2
        """,
        conversation_id,
        user_id,
    )

    return result == "DELETE 1"


async def get_messages(
    conversation_id: int,
    user_id: int,
    db: asyncpg.Connection,
) -> list | None:

    conversation = await db.fetchrow(
        """
        SELECT id FROM conversations
        WHERE id = $1
        AND user_id = $2
        """,
        conversation_id,
        user_id,
    )

    if not conversation:
        return None

    messages = await db.fetch(
        """
        SELECT id, conversation_id, role, content, created_at
        FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at ASC
        """,
        conversation_id,
    )

    return [dict(m) for m in messages]


async def create_message(
    conversation_id: int,
    user_id: int,
    content: str,
    db: asyncpg.Connection,
) -> dict:

    # check conversation belongs to this user
    conversation = await db.fetchrow(
        """
        SELECT id FROM conversations
        WHERE id = $1
        AND user_id = $2
        """,
        conversation_id,
        user_id,
    )

    if not conversation:
        return None

    # save user message
    await db.fetchrow(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES ($1, $2, $3)
        RETURNING id, conversation_id, role, content, created_at
        """,
        conversation_id,
        "user",
        content,
    )
    ai_response = call_llm(content)
    message = message = await db.fetchrow(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES ($1, 'assistant', $2)
        RETURNING id, conversation_id, role, content, created_at
        """,
        conversation_id,
        ai_response,
    )

    return dict(message)
