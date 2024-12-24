from infrastructure.db.connection import pg_connection
from persistent.db.mentor import Mentor
from sqlalchemy import insert, select, UUID
from typing import cast


class MentorRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def create_mentor(self,
                            tg_id: str,
                            name: str,
                            info: str) -> UUID | None:
        stmp = insert(Mentor).values({"telegram_id": tg_id, "name": name, "info": info})

        async with self._sessionmaker() as session:
            result = await session.execute(stmp)
            hackathon_id = result.inserted_primary_key[0]
            await session.commit()

        return hackathon_id

    async def get_all_mentors(self) -> list[Mentor]:
        stmt = select(Mentor)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            mentors = [row[0] for row in rows]
            return mentors

    async def get_mentor_by_id(self, mentor_id: UUID) -> Mentor | None:
        stmp = select(Mentor).where(cast("ColumnElement[bool]", Mentor.id == mentor_id)).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        return row[0] if row else None