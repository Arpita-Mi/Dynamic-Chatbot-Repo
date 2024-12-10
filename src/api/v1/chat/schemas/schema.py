from fastapi import Query, Form
from pydantic import BaseModel 
from typing import List, Optional, Dict  
from datetime import datetime
from field_validation.form_validation import FormValidation

class Message(BaseModel):
    question_key: int
    msg_text: str
    msg_type: int
    response : str = None
    response_time :datetime = None
    next_question: Optional[Dict[str, int]] = None  
    options: Optional[List[Dict[str,str]]] = None
  



class Payload(FormValidation):

    def __init__(self,
    room_id : int = Form(None),
    sender_id :int = Form(None),
    id :  int = Form(None),
    message: str = Form(None),
    question_key :int =  Form(),
    current_question_id : int = Form(None),
    msg_type : int = Form(None)):
        self.room_id = room_id
        self.sender_id =  sender_id
        self.id = id
        self.message = message
        self.question_key = question_key
        self.current_question_id = current_question_id
        self.msg_type = msg_type



class RetrivePaylaod(BaseModel):
   room_id : int