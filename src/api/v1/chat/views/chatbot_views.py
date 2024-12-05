from fastapi import APIRouter, status, Request, Header, Depends, Query
from typing import List
from config.config import settings
from src.api.v1.chat.schemas.schema import Payload , Message,RetrivePaylaod
from src.api.v1.chat.services.mongo_services import chatbot_insert_message , fetch_question_data_from_mongo , update_message
from src.api.v1.chat.services.chatbot_services import get_question_field_map_resposne , save_respose_db
from database.db_mongo_connect import MongoUnitOfWork
from database.db_connection import get_service_db_session
from datetime import datetime
from pymongo import DESCENDING

router = APIRouter(prefix="/statistic")



@router.post("/chatbot/insert_chatbot_conversation", summary="save chatbot conversation",
             status_code=status.HTTP_200_OK)
async def insert_chatbot_conversation(request: Request, scr: List[Message], language_id: str = Header(None)):
    """
    API to conversation with Copilots Question.
    """
    language_id = int(request.headers.get('language-id', '1'))
    try:  
        client, db = MongoUnitOfWork().mdb_connect()
        collection_name = "online_shopping_chatbot"    
        current_time = datetime.now()
        response_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        response_data = []
        for message in scr:
            message_dict = {
                "question_key" : message.question_key,
                'msg_text': message.msg_text,
                'msg_type': message.msg_type,
                "response" : message.response,
                "response_time" : message.response_time,
                'options' : message.options,
                'next_question': message.next_question
            }
            message_dict["language-id"] = language_id
            message_dict["question_key"] = message.question_key

            response_data.append(
                message_dict
            # "timestamp": datetime.now()
            
            )
        
        message_resposne = await chatbot_insert_message(db, collection_name, response_data)

    except Exception as e:
        return (str(e))
    else:
        return (response_data)




@router.post("/chatbot/dynamic_chatbot_conversation", summary="Dynamic chatbot conversation",
             status_code=status.HTTP_200_OK)
async def dynamic_chatbot_conversation(request: Request, scr: Payload, language_id: str = Header(1)):
    """
    API to retrieve chatbot conversation by question key and save dynamic response.
    """
    try:
        language_id = int(request.headers.get('language-id', '1'))

        service_db_credentials = {
            "username": settings.SERVICE_DB_USER,
            "password": settings.SERVICE_DB_PASSWORD,
            "hostname": settings.SERVICE_DB_HOSTNAME,
            "port": settings.SERVICE_DB_PORT,
            "db_name": settings.SERVICE_DB
        }
        service_db_session = await get_service_db_session(service_db_credentials)

        client, db = MongoUnitOfWork().mdb_connect()
        user_collection = "user_data"
        time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        def create_message(question_key: int) -> dict:
            return {
                "room_id": scr.room_id,
                "sender_id": scr.sender_id,
                "message": fetch_question_data_from_mongo(question_key=question_key),
                "created_at": time_now
            }

        if scr.question_key == 1 and scr.msg_type is None:
            ques = create_message(scr.question_key)
            db[user_collection].insert_one(ques)
            if "_id" in ques:
                ques["_id"] = str(ques["_id"])
            res = {
                    "room_id": scr.room_id,
                    "sender_id": scr.sender_id,
                    "message": fetch_question_data_from_mongo(
                        question_key=scr.question_key
                    )
                }
            return res

        elif scr.msg_type == 2:
            latest_message = db[user_collection].find_one(
                {"room_id": scr.room_id}, sort=[("created_at", DESCENDING)]
            )

            if latest_message:
                update_values = {
                    "message.response": "Yes",
                    "message.response_time": time_now
                }
                db[user_collection].update_one(
                    {"_id": latest_message["_id"]}, {"$set": update_values}
                )

                ques = create_message(scr.question_key)
                db[user_collection].insert_one(ques)
                if "_id" in ques:
                    ques["_id"] = str(ques["_id"])

                res = {
                    "room_id": scr.room_id,
                    "sender_id": scr.sender_id,
                    "message": fetch_question_data_from_mongo(
                        question_key=scr.question_key
                    )
                }
                return res

        return {"error": "Invalid input"}

    except Exception as e:
        return {"error": str(e)}



@router.get("/chatbot/retrive_conversation", summary="dynamic chatbot conversation",
            status_code=status.HTTP_200_OK)
async def retrive_convsersation(request: Request, room_id :int ,language_id: str = Header(1)):
    room_list = get_question_data_from_room(room_id)
    return room_list





def get_question_data_from_room(room_id):
    client, db = MongoUnitOfWork().mdb_connect()
    user_collection  =  "user_data"
    room_data = db[user_collection].find({"room_id": room_id },
                            {"room_id":0 ,"_id": 0})
    room_list = list(room_data)
    return room_list




