"""CRUD operations for User."""

import hashlib
import hmac
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


def hash_password(password: str) -> str:
    """Hashes a password."""
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 390000)
    return f"{salt.hex()}:{derived_key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password."""
    salt_hex, hash_hex = hashed_password.split(":", 1)
    salt = bytes.fromhex(salt_hex)
    expected_hash = bytes.fromhex(hash_hex)
    candidate_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 390000)
    return hmac.compare_digest(expected_hash, candidate_hash)


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Creates a new user."""
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Gets a user by ID."""
    result = await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.id == user_id)
    )
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Gets a user by username."""
    result = await db.execute(
        select(User).filter(User.username == username)
    )
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Gets a user by email."""
    result = await db.execute(
        select(User).filter(User.email == email)
    )
    return result.scalars().first()


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Gets all users."""
    result = await db.execute(
        select(User).options(selectinload(User.profile)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User | None:
    """Updates a user."""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Deletes a user."""
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    await db.commit()
    return True
