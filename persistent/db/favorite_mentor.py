from persistent.db.base import Base, WithId
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class FavoriteMentor(Base, WithId):
    __tablename__ = "favorite_mentors"
    __table_args__ = (UniqueConstraint("user_id", "mentor_id"),)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("mentors.id"))
    mentor = relationship("Mentor")
