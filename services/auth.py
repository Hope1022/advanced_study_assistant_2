from datetime import datetime, timezone

import asyncpg
from schemas.user import UserRegisterSchema, UserLoginSchema
from schemas.token import TokenSchema
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
)
from core.exceptions import (
    InvalidCredentialsException,
    EmailAlreadyExistsException,
    InvalidTokenException,
    TokenTypeMismatchException,
)


async def register_user(
    data: UserRegisterSchema,
    db: asyncpg.Connection,
) -> TokenSchema:

    # check if email already exists
    existing_user = await db.fetchrow(
        "SELECT id FROM users WHERE email = $1", data.email
    )

    if existing_user:
        raise EmailAlreadyExistsException

    password_hash = hash_password(data.password)

    # insert user and get the new id back
    new_user = await db.fetchrow(
        """
        INSERT INTO users (email, password_hash)
        VALUES ($1, $2)
        RETURNING id
        """,
        data.email,
        password_hash,
    )

    token_data = {"sub": str(new_user["id"])}

    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # insert session
    await db.execute(
        """
        INSERT INTO sessions (user_id, refresh_token)
        VALUES ($1, $2)
        """,
        new_user["id"],
        refresh_token,
    )

    return {
    "access_token": access_token,
    "refresh_token": refresh_token,
}


async def login_user(
    data: UserLoginSchema,
    db: asyncpg.Connection,
) -> TokenSchema:

    user = await db.fetchrow(
        "SELECT id, password_hash, is_active FROM users WHERE email = $1",
        data.email,
    )

    if not user:
        raise InvalidCredentialsException

    if not verify_password(data.password, user["password_hash"]):
        raise InvalidCredentialsException

    if not user["is_active"]:
        raise InvalidCredentialsException

    # update last login
    await db.execute(
        "UPDATE users SET last_login = $1 WHERE id = $2",
        datetime.now(timezone.utc),
        user["id"],
    )

    token_data = {"sub": str(user["id"])}

    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    await db.execute(
        """
        INSERT INTO sessions (user_id, refresh_token)
        VALUES ($1, $2)
        """,
        user["id"],
        refresh_token,
    )

    return {
    "access_token": access_token,
    "refresh_token": refresh_token,
}

#the front-end automatically calls this when the acces token is expired

async def refresh_access_token(
    refresh_token: str,
    db: asyncpg.Connection,
) -> TokenSchema:

    payload = decode_token(refresh_token)

    if payload is None:
        raise InvalidTokenException

    if not verify_token_type(payload, "refresh"):
        raise TokenTypeMismatchException

    session = await db.fetchrow(
        """
        SELECT id FROM sessions
        WHERE refresh_token = $1
        AND is_revoked = FALSE
        """,
        refresh_token,
    )

    if not session:
        raise InvalidTokenException

    token_data = {"sub": payload["sub"]}
    access_token=create_access_token(token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

async def logout_user(
    refresh_token: str,
    db: asyncpg.Connection,
) -> None:

    await db.execute(
        """
        UPDATE sessions
        SET is_revoked = TRUE
        WHERE refresh_token = $1
        """,
        refresh_token,
    )