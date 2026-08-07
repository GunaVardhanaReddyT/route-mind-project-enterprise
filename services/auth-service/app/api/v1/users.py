from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
from sqlalchemy import select

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user