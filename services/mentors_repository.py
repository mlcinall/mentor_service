from infrastructure.db.connection import pg_connection
from persistent.db.mentor import Mentor
from sqlalchemy import insert, select


class MentorRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()

    async def add_mentor(self, tg_id: str, name: str, info: str) -> None:
        stmp = insert(Mentor).values({"telegram_id": tg_id, "name": name, "info": info})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_mentors_list(self) -> list[int]:
        stmp = select(Mentor.id)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)
            # Преобразуем результат в список id

        id_list = [row[0] for row in resp]
        return id_list
