from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Integer, text, JSON

from database.database_manager import Base

class QuestionFieldsMap(Base):
    __tablename__ = "question_fields_map"
    __table_args__ = {'extend_existing': True}  # Allow redefining the table


    current_question_key = Column(Integer,primary_key=True,autoincrement=True)
    fields = Column(String)
    msg_type = Column(Integer)



def dynamic_question_filed_map(table_name, fields):
    """
    Creates a dynamic SQLAlchemy model with the specified table name and fields.
    """
    class_attrs = {
        '__tablename__': table_name,
        '__table_args__': {'extend_existing': True},
        'id': Column(Integer, primary_key=True, autoincrement=True)  # Default primary key
    }
    for field_name, field_type in fields.items():
        class_attrs[field_name] = Column(field_type)
    return type(table_name, (Base,), class_attrs)

