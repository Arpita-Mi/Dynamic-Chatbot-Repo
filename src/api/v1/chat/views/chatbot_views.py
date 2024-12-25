from fastapi import APIRouter, status, Request, Header, Depends, Query, HTTPException, UploadFile , File,Form 
from typing import List
from config.config import settings
from src.api.v1.chat.schemas.schema import Payload , Message,RetrivePaylaod
from src.api.v1.chat.repositories.chatbot_repository import save_question_payload_query, fetch_question_payload_query
from src.api.v1.chat.services.mongo_services import chatbot_insert_message , fetch_question_data_from_mongo 
from src.api.v1.chat.services.chatbot_services import create_message, construct_response , get_question_field_map_resposne ,\
update_latest_message,save_respose_db , update_latest_message_with_image , generate_image_url , get_question_data_from_room,\
create_dynamic_models
from src.api.v1.chat.constants import constant
from database.db_mongo_connect import MongoUnitOfWork
from database.db_connection import get_service_db_session
from src.api.v1.chat.models.models import QuestionFieldsMap
import os
import shutil
from datetime import datetime
from pymongo import DESCENDING

router = APIRouter(prefix="/statistic")



@router.post("/chatbot/insert_chatbot_conversation", summary="save chatbot conversation",
             status_code=status.HTTP_200_OK)

async def insert_chatbot_conversation(request: Request, scr: List[Message], language_id: str = Header(None)):
    """
    API to Insert Question paylaod
    """
    language_id = int(request.headers.get('language-id', '1'))
    try:  
        client, db = MongoUnitOfWork().mdb_connect()
        collection_name = constant.MASTER_COLLECTION   
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
async def dynamic_chatbot_conversation(request: Request, scr: Form = Depends(Payload), language_id: str = Header(1),
                                   image :List[UploadFile]=File(None) 
                                ):
    """
    API to retrieve chatbot conversation by msg_type and save dynamic response.
    """
    try:
        language_id = int(request.headers.get('language-id', '1'))
        # Database credentials and sessions
        service_db_credentials = {  
            "username": settings.SERVICE_DB_USER,
            "password": settings.SERVICE_DB_PASSWORD,
            "hostname": settings.SERVICE_DB_HOSTNAME,
            "port": settings.SERVICE_DB_PORT,
            "db_name": settings.SERVICE_DB
        }
        service_db_session = await get_service_db_session(service_db_credentials)

        client, db = MongoUnitOfWork().mdb_connect()
        user_collection = constant.USER_COLLECTION

        latest_message = db[user_collection].find_one(
            {"room_id": scr.room_id}, sort=[("created_at", DESCENDING)]
        )

        if scr.question_key == 1 and scr.msg_type is None:
            ques = create_message(scr, scr.question_key)
            db[user_collection].insert_one(ques)
            if "_id" in ques:
                ques["_id"] = str(ques["_id"])

            response = await get_question_field_map_resposne(service_db_session=service_db_session ,question_key = scr.question_key)
            if response:
                ques["id"] = scr.id
                ques["response"] = scr.message
                ques["current_question_id"] = scr.question_key
                user_details = await save_respose_db(service_db_session=service_db_session ,question_data=ques,response=response)

        elif scr.msg_type in [1, 2 ,3, 4]:     #[1:text , 2:boolean , 3:multiple selection]
            #UPDATE THE RESPOSNE TO MONGO
            if latest_message:
                update_latest_message(db, latest_message, scr.message, user_collection)
            
            #INSERT QUESTION TO MONGO
            ques = create_message(scr, scr.question_key) #fetch the question details from master db(mongo) and create a dict 
            db[user_collection].insert_one(ques)
            if "_id" in ques:
                ques["_id"] = str(ques["_id"])

            
            #SAVE RESPOSNE TO DATABASE
            response = await get_question_field_map_resposne(service_db_session=service_db_session ,question_key = scr.question_key)
            if response:
                ques["id"] = scr.id
                ques["response"] = scr.message
                ques["current_question_id"] = scr.current_question_id
                user_details = await save_respose_db(service_db_session=service_db_session ,question_data=ques,response=response)

        elif scr.msg_type == 5:
            if latest_message:
                if image:  # Raw image 
                    image_data =  image
                    image_url = update_latest_message_with_image(db, latest_message, image_data, user_collection)
                else:
                    update_latest_message(db, latest_message, scr.message, user_collection)

            ques = create_message(scr, scr.question_key) #fetch the question details from master db(mongo) and create a dict 
            db[user_collection].insert_one(ques)
            if "_id" in ques:
                ques["_id"] = str(ques["_id"])

            #SAVE RESPOSNE TO DATABASE
            update_list = []
            image_list = generate_image_url(image_data)
            for i in image_list:
      
                update_list.append( i["image_url"])
            response = await get_question_field_map_resposne(service_db_session=service_db_session ,question_key = scr.question_key)
            if response:
                ques["id"] = scr.id
                ques["response"] = update_list
                ques["current_question_id"] = scr.current_question_id
                user_details = await save_respose_db(service_db_session=service_db_session ,question_data=ques,response=response)


        return construct_response(scr, scr.question_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@router.get("/chatbot/retrive_conversation", summary="dynamic chatbot conversation",
            status_code=status.HTTP_200_OK)
async def retrive_convsersation(request: Request, room_id :int ,language_id: str = Header(1)):
    room_list = get_question_data_from_room(room_id)
    return room_list




@router.post("/chatbot/save_chatbot_conversation_db", summary="save_chatbot_conversation_db",
             status_code=status.HTTP_200_OK)
async def save_chatbot_conversation_db(request: Request, scr: List[Message],Organization_Name:str, language_id: str = Header(None)):
    """
    API to Insert Question paylaod
    """
    language_id = int(request.headers.get('language-id', '1'))
    try:  
        service_db_credentials = {  
            "username": settings.SERVICE_DB_USER,
            "password": settings.SERVICE_DB_PASSWORD,
            "hostname": settings.SERVICE_DB_HOSTNAME,
            "port": settings.SERVICE_DB_PORT,
            "db_name": settings.SERVICE_DB
        }
        service_db_session = await get_service_db_session(service_db_credentials)
        question_entries = []
        current_question_key = 1

        for message in scr:
            field_value = f"question_answer_{message.question_key}"
            question_entry = {
                "current_question_key": current_question_key,
                "fields": field_value,
                "msg_type": message.msg_type
            }
            question_entries.append(question_entry)
            current_question_key += 1
                
            await save_question_payload_query(service_db_session,question_entry)

        create_dynamic_models(question_entries,Organization_Name)
  
        return {"status": "success", "message": "Data saved and new file created."}
    except Exception as e:
        return (str(e))

#FETCH THE DETAILS FROM DB 
@router.get("/chatbot/get_question_paylaod_detail", summary="save_chatbot_conversation_db",
             status_code=status.HTTP_200_OK)
async def get_question_paylaod_detail(request: Request,language_id: str = Header(None)):
    """
    API to Insert Question paylaod
    """
    language_id = int(request.headers.get('language-id', '1'))
    try:  
        service_db_credentials = {  
            "username": settings.SERVICE_DB_USER,
            "password": settings.SERVICE_DB_PASSWORD,
            "hostname": settings.SERVICE_DB_HOSTNAME,
            "port": settings.SERVICE_DB_PORT,
            "db_name": settings.SERVICE_DB
        }
        service_db_session = await get_service_db_session(service_db_credentials)
        response_data = []
       
        question_respsone =  fetch_question_payload_query(service_db_session)
        response_data = [
            { "current_question_key": item.current_question_key,"fields": item.fields , "msg_type" : item.msg_type}
            for item in question_respsone
        ]
        print(response_data)
    except Exception as e:
        return (str(e))
    else:
        return response_data


