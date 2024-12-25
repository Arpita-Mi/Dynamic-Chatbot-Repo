from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Integer, text, JSON

from database.database_manager import Base


class IncidentDetails(Base):
    __tablename__ = 'incident_details'
    __table_args__ = {'extend_existing': True}  # Allow redefining the table

    id = Column(Integer, primary_key=True, unique=True)