from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Integer, text, JSON

from database.database_manager import Base

class QuestionFieldsMap(Base):
    __tablename__ = "question_fields_map"

    current_question_key = Column(Integer,primary_key=True, unique=True)
    fields = Column(String)



class UserResponse(Base):
    __tablename__ = "user_resposne"

    id = Column(Integer, primary_key=True,unique=True ,  index=True)
    user_res = Column(String)
    user_class =  Column(String)
    user_name = Column(String)
    user_region= Column(String)
    user_int= Column(String)
