from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer , String

from database.database_manager import Base


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

