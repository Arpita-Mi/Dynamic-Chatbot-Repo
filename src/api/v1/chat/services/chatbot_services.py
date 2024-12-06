from src.api.v1.chat.repositories.chatbot_repository import get_question,save_user_response
from src.api.v1.chat.schemas.schema import Payload
from src.api.v1.chat.services.mongo_services import fetch_question_data_from_mongo

from datetime import datetime

async def get_question_field_map_resposne(question_key :int , service_db_session = None):
    initial_question = await get_question(service_db_session ,question_key)
    message = {
        "question_key" : initial_question.current_question_key,
        "fields": initial_question.fields,
        
    }
    return message

async def save_respose_db(question_data : dict , response :dict,service_db_session = None):
   
    initial_question = await save_user_response(service_db_session ,question_data,response)
    # for initial_question in initial_questions:
    initial_question = {"id" : initial_question.id,
                        # "question_key" : question_data["question_key"],
                        # "msg_text" : question_data["msg_text"],
                        # "msg_type" :question_data["msg_type"],
                        # "next_question" :question_data["next_question"],
                        # "language-id" : question_data["language-id"] 
                        }
    return initial_question



def create_message(scr: Payload, question_key: int) -> dict:
    time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return {
        "room_id": scr.room_id,
        "sender_id": scr.sender_id,
        "message": fetch_question_data_from_mongo(question_key=question_key),
        "created_at": time_now
    }

# async def save_response_to_db(service_db_session, scr, question_key) -> None:
#     response = await get_question_field_map_resposne(
#         service_db_session=service_db_session,
#         question_key=question_key
#     )
#     if response:
#         ques = {
#             "id": scr.id,
#             "response": scr.message,
#             "current_question_id": scr.current_question_id
#         }
#         return await save_user_response(service_db_session,ques,response)
#     return None

def update_latest_message( db,  latest_message, response_message, user_collection) -> None:
    time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    update_values = {
        "message.response": response_message,
        "message.response_time": time_now
    }
    db[user_collection].update_one(
        {"_id": latest_message["_id"]}, {"$set": update_values}
    )

def construct_response(scr: Payload, question_key: int) -> dict:
    return {
        "room_id": scr.room_id,
        "sender_id": scr.sender_id,
        "message": fetch_question_data_from_mongo(
            question_key=question_key
        )
    }



