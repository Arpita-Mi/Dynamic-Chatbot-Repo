from fastapi import Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class Message(BaseModel):
    question_key: int
    msg_text: str
    msg_type: int
    response : str = None
    response_time :datetime = None
    next_question: Optional[Dict[str, int]] = None  
    options: Optional[List[Dict[str,str]]] = None
    # options_response: Optional[List[str]] = None
    # statistic_id: int
    # current_sequence_id: int


class ChatMessage(BaseModel):
    room_id: str
    sender_id: str
    message: Message
    content_type: int
    attachment: Optional[str] = None
    is_read_by: List[str] = []
    is_edited: Optional[bool] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class MessageInDB(Message):
 id: str


class Payload(BaseModel):
    room_id : Optional[int] = None
    sender_id :Optional[int] = None
    id :  Optional[int] = None
    message: Optional[str] = None
    question_key :int
    current_question_id : Optional[int] = None
    msg_type : Optional[int] = None

class RetrivePaylaod(BaseModel):
   room_id : int