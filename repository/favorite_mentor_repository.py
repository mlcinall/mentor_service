from infrastructure.db.connection import pg_connection
from persistent.db.favorite_mentor import FavoriteMentor
from sqlalchemy import insert, select, delete, UUID
from typing import Optional, cast
from sqlalchemy.sql import ColumnElement


class FavoriteMentorRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def add_favorite(self, user_id: UUID, mentor_id: UUID) -> Optional[UUID]:
        stmt = insert(FavoriteMentor).values({
            "user_id": user_id,
            "mentor_id": mentor_id,
        })
        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            fav_id = result.inserted_primary_key[0]
            await session.commit()
        return fav_id

    async def remove_favorite(self, user_id: UUID, mentor_id: UUID) -> None:
        stmt = delete(FavoriteMentor).where(
            cast(ColumnElement[bool], FavoriteMentor.user_id == user_id),
            cast(ColumnElement[bool], FavoriteMentor.mentor_id == mentor_id),
        )
        async with self._sessionmaker() as session:
            await session.execute(stmt)
            await session.commit()

    async def get_favorites(self, user_id: UUID) -> list[FavoriteMentor]:
        stmt = select(FavoriteMentor).where(
            cast(ColumnElement[bool], FavoriteMentor.user_id == user_id)
        )
        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)
            rows = resp.fetchall()
            favorites = [row[0] for row in rows]
            return favorites
