from persistent.db.base import Base, WithId
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship


class Mentor(Base, WithId):
    __tablename__ = "mentors"

    telegram_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    info = Column(Text, nullable=False)
    about = Column(Text, nullable=True)
    specification = Column(Text, nullable=True)
    role = Column(Text, nullable=True)
    experience_periods = Column(Text, nullable=True)
    hackathons = Column(Text, nullable=True)
    work = Column(Text, nullable=True)
    requests = relationship("Request", back_populates="mentor")
    time = relationship("MentorTime", back_populates="mentor")