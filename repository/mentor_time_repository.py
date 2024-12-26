from infrastructure.db.connection import pg_connection
from persistent.db.mentor_time import MentorTime
from sqlalchemy import insert, select, UUID, update
from typing import cast, Optional
from datetime import time as Time


class MentorTimeRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def create_new_mentor_time(self,
                            day: int,
                            time_start: Time,
                            time_end: Time,
                            mentor_id: UUID) -> Optional[UUID]:
        # if day not in range(1, 8):
        #     raise ValueError("error: day out of range")


        stmp = insert(MentorTime).values({"day": day, "time_start": time_start,
                                          "time_end": time_end, "mentor_id": mentor_id})

        async with self._sessionmaker() as session:
            result = await session.execute(stmp)
            mentor_time_id = result.inserted_primary_key[0]
            await session.commit()

        return mentor_time_id

    async def update_mentor_time(self, mentor_time_id: UUID,
                                 time_start: Time, time_end: Time) -> None:
        stmp = (update(MentorTime).where(cast("ColumnElement[bool]",MentorTime.id == mentor_time_id))
                .values(time_start=time_start, time_end=time_end))

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_all_mentor_time(self) -> list[MentorTime]:
        stmt = select(MentorTime)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            mentor_time_list = [row[0] for row in rows]
            return mentor_time_list

    async def get_all_mentor_time_by_mentor_id(self, mentor_id: UUID) -> Optional[list[MentorTime]]:
        stmt = select(MentorTime).where(cast("ColumnElement[bool]", MentorTime.mentor_id == mentor_id))

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            mentor_time_list = [row[0] for row in rows]
            return mentor_time_list

    async def get_mentor_time_by_id(self, mentor_time_id: UUID) -> Optional[MentorTime]:
        stmp = select(MentorTime).where(cast("ColumnElement[bool]", MentorTime.id == mentor_time_id)).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        return row[0] if row else None