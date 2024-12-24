from persistent.db.base import Base, WithId
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Boolean, Integer, Time, ForeignKey
from sqlalchemy.orm import relationship


class MentorTime(Base, WithId):
    __tablename__ = "mentor_time"

    day = Column(Integer, nullable=True)  # possible call day number (0 -- Monday, 1 -- Tuesday etc)
    time_start = Column(Time, nullable=True)
    time_end = Column(Time, nullable=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"))
    mentor = relationship("Mentor", back_populates="time")
