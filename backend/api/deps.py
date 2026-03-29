from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database import async_session

api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def require_admin_key(key: str | None = Security(api_key_header)) -> str:
    if not key or key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    return key
