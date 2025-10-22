from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)

    children = relationship("Activity", back_populates="parent")
    parent = relationship("Activity", back_populates="children", remote_side=[id])

    organizations = relationship("Organization", secondary="organization_activities", back_populates="activities")