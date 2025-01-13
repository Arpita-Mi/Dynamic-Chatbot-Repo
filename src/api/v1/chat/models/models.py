from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey, Integer, text, JSON

from database.database_manager import Base

# class QuestionFieldsMap(Base):
#     __tablename__ = "question_fields_map"

#     current_question_key = Column(Integer,primary_key=True,autoincrement=True)
#     fields = Column(String)
#     msg_type = Column(Integer)



# class UserResponse(Base):
#     __tablename__ = "user_resposne"

#     id = Column(Integer, primary_key=True,unique=True , autoincrement=True,  index=True)
#     email = Column(String)
#     product_category =  Column(String)
#     price = Column(String)
#     product= Column(String)
#     selected_products = Column(String)
#     urls = Column(JSON)
#     Thanks = Column(String)
#     initial = Column(String)