from infrastructure.db.connection import pg_connection
from persistent.db.mentor_time import MentorTime
from sqlalchemy import insert, select, UUID
from typing import cast
from datetime import time as Time


class MentorRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def create_mentor_time(self,
                            day: int,
                            time: Time,
                            mentor_id: UUID) -> UUID | None:
        if day not in range(1, 8):
            raise ValueError("error: day out of range")
        stmp = insert(MentorTime).values({"day": day, "time": time, "mentor_id": mentor_id})

        async with self._sessionmaker() as session:
            result = await session.execute(stmp)
            mentor_time_id = result.inserted_primary_key[0]
            await session.commit()

        return mentor_time_id

    async def get_all_mentor_time(self) -> list[MentorTime]:
        stmt = select(MentorTime)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            mentor_time_list = [row[0] for row in rows]
            return mentor_time_list

    async def get_all_mentor_time_by_mentor_id(self, mentor_id: UUID) -> list[MentorTime] | None:
        stmt = select(MentorTime).where(cast("ColumnElement[bool]", MentorTime.mentor_id == mentor_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            mentor_time_list = [row[0] for row in rows]
            return mentor_time_list

    async def get_mentor_time_by_id(self, mentor_time_id: UUID) -> MentorTime | None:
        stmp = select(MentorTime).where(cast("ColumnElement[bool]", MentorTime.id == mentor_time_id)).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        return row[0] if row else None