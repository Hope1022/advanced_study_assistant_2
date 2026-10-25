from fastapi import APIRouter, Depends, status
import asyncpg
 
from database.database import get_db, get_authenticated_db
from schemas.user import UserRegisterSchema, UserLoginSchema
from schemas.token import TokenSchema, RefreshTokenSchema
from services import auth
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
#called by front-end register but user button
@router.post(
    "/register",
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegisterSchema,
    db: asyncpg.Connection = Depends(get_db),
):
   
    return await auth.register_user(data, db)
 
@router.post(
    "/login",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: UserLoginSchema,
    db: asyncpg.Connection = Depends(get_db),
):
    return await auth.login_user(data, db)

#called by insider thing the browser calls it
@router.post(
    "/refresh",
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    data: RefreshTokenSchema,#the refresh token
    db: asyncpg.Connection = Depends(get_db),
):
    return await auth.refresh_access_token(data.refresh_token, db)
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    data: RefreshTokenSchema,
    db: asyncpg.Connection = Depends(get_db),
):
    await auth.logout_user(data.refresh_token, db)
    return {"message": "Logged out successfully."}