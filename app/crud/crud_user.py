import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.password import get_password_hash
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_by_email(db: AsyncSession, *, email: str) -> User | None:
    """Retrieve a user by their email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_by_oid(db: AsyncSession, *, oidc_oid: str) -> User | None:
    """Retrieve a user by their OIDC OID."""
    result = await db.execute(select(User).where(User.oidc_oid == oidc_oid))
    return result.scalars().first()


async def get_by_id(db: AsyncSession, *, id: uuid.UUID) -> User | None:
    """Retrieve a user by their ID."""
    result = await db.execute(select(User).where(User.id == id))
    return result.scalars().first()


async def create(db: AsyncSession, *, obj_in: UserCreate):
    """Create a new user in the database."""
    user_data = obj_in.model_dump()
    plain_password = user_data.pop("password")
    user_data["password_hash"] = get_password_hash(plain_password)

    db_obj = User(**user_data)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, *, db_obj: User, obj_in: UserUpdate) -> User:
    """Update an existing user in the database."""
    user_data = obj_in.model_dump(exclude_unset=True)

    if "password" in user_data:
        db_obj.password_hash = get_password_hash(user_data.pop("password"))

    for field, value in user_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
