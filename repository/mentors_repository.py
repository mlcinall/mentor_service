from infrastructure.db.connection import pg_connection
from persistent.db.mentor import Mentor
from sqlalchemy import insert, select, UUID, update, func
from typing import cast, Optional


class MentorRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def create_mentor(self,
        tg_id: str,
        name: str,
        info: str,
        about: str = None,
        specification: str = None
    ) -> Optional[UUID]:
        stmp = insert(Mentor).values({
            "telegram_id": tg_id,
            "name": name,
            "info": info,
            "about": about,
            "specification": specification
        })
        async with self._sessionmaker() as session:
            result = await session.execute(stmp)
            mentor_id = result.inserted_primary_key[0]
            await session.commit()
        return mentor_id

    async def get_all_mentors(self) -> list[Mentor]:
        stmt = select(Mentor)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)

            rows = resp.fetchall()
            mentors = [row[0] for row in rows]
            return mentors

    async def get_mentor_by_id(self, mentor_id: UUID) -> Optional[Mentor]:
        stmp = select(Mentor).where(Mentor.id == mentor_id).limit(1)
        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)
        row = resp.fetchone()
        return row[0] if row else None

    async def get_mentor_by_tg_id(self, tg_id: str) -> Optional[Mentor]:
        stmp = select(Mentor).where(Mentor.telegram_id == tg_id).limit(1)
        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)
        row = resp.fetchone()
        return row[0] if row else None

    async def update_mentor_info(self, mentor_id: UUID, info: str) -> None:
        stmp = update(Mentor).where(Mentor.id == mentor_id).values(info=info)
        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def update_mentor_external_fields(
        self,
        mentor_id: UUID,
        about: Optional[str],
        specification: Optional[str],
        name: Optional[str],
        telegram_id: Optional[str],
    ) -> None:
        stmp = update(Mentor).where(Mentor.id == mentor_id).values(about=about, specification=specification, name=name, telegram_id=telegram_id)
        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def update_mentor_additional_fields(
        self,
        mentor_id: UUID,
        about: Optional[str] = None,
        specification: Optional[str] = None,
        role: Optional[str] = None,
        experience_periods: Optional[str] = None,
        hackathons: Optional[str] = None,
        work: Optional[str] = None,
    ) -> None:
        values: dict[str, Optional[str]] = {}
        if about is not None:
            values["about"] = about
        if specification is not None:
            values["specification"] = specification
        if role is not None:
            values["role"] = role
        if experience_periods is not None:
            values["experience_periods"] = experience_periods
        if hackathons is not None:
            values["hackathons"] = hackathons
        if work is not None:
            values["work"] = work
        if not values:
            return
        stmp = update(Mentor).where(Mentor.id == mentor_id).values(**values)
        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_mentors_by_name(self, name: str) -> list[Mentor]:
        """
        Поиск менторов по имени (частичное совпадение, регистронезависимо).
        """
        stmt = select(Mentor).where(func.lower(Mentor.name).like(f"%{name.lower()}%"))
        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)
            rows = resp.fetchall()
            mentors = [row[0] for row in rows]
            return mentors

    async def get_mentors_by_specification(self, specification: str) -> list[Mentor]:
        """
        Поиск менторов по роли (specification, частичное совпадение, регистронезависимо).
        """
        stmt = select(Mentor).where(func.lower(Mentor.specification).like(f"%{specification.lower()}%"))
        async with self._sessionmaker() as session:
            resp = await session.execute(stmt)
            rows = resp.fetchall()
            mentors = [row[0] for row in rows]
            return mentors
