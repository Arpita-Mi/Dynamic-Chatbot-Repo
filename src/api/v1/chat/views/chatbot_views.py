from fastapi import APIRouter, status, Request, Header, Depends, Query, HTTPException, UploadFile , File,Form 
from typing import List
from src.api.v1.chat.schemas.schema import Payload , Message
from src.api.v1.chat.repositories.chatbot_repository import fetch_question_payload_query
from src.api.v1.chat.services.mongo_services import chatbot_save_message_to_mongo_redis ,create_message ,construct_response ,update_latest_message, update_latest_message_with_image ,\
generate_image_url , get_question_data_from_room , get_msg_type_from_master_mongo
from src.api.v1.chat.services.chatbot_services import get_question_field_map_resposne ,save_respose_db ,create_dynamic_models ,\
create_question_field_map_dynamic_models , clear_pycache  , conversation_operations 
from database.db_mongo_connect import create_mongo_connection
from database.db_connection import create_service_db_session
from datetime import datetime
from src.api.v1.chat.constants.constant import MsgType
from pymongo import DESCENDING
from database.db_mongo_connect import MongoUnitOfWork
from logger.logger import logger , log_format
router = APIRouter(prefix="/statistic")



@router.post("/chatbot/insert_chatbot_conversation", summary="save chatbot conversation",
             status_code=status.HTTP_200_OK)

async def insert_chatbot_conversation(request: Request, scr: List[Message], ChatbotName = str,language_id: str = Header(1)):
    """
    Saves chatbot conversation data to MongoDB and SQL, and caches frequently asked questions in Redis.

    **Request:**
        request (Request): The incoming HTTP request.
        scr (List[Message]): The payload containing the user's input data.
        ChatbotName (str): The name of the chatbot.
        language_id (str): The language ID (default is 1).

    **Process:**
    - Stores conversation in MongoDB with metadata.
    - Caches data in Redis for fast retrieval.
    - Dynamically updates SQL tables with new question-answer mappings.

    **Response:**
    - Returns the list of saved messages with relevant details.

    **Error Handling:**
    - Returns error message if any issue occurs during processing.    
    """



    logger.info(log_format(msg="insert chatbot conversation api call"))
    # language_id = int(request.headers.get('language-id', '1'))

    try:
        # Prepare database credentials
        clear_pycache()
        service_db_session, _= await create_service_db_session()        

        db , master_collection , _ = create_mongo_connection()
        master_collection = f"{ChatbotName}{master_collection}"
        logger.debug(f"Connecting to MongoDB with collection name: {master_collection}")

        save_mongo_paylaod = []
        # Current timestamp
        current_time = datetime.now()
        response_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Prepare response data and insert into MongoDB
        for message in scr:
            save_mongo_paylaod.append({
                "question_key": message.question_key,
                "msg_text": message.msg_text,
                "msg_type": message.msg_type,
                "response": message.response,
                "response_time": message.response_time,
                "options": message.options,
                "next_question": message.next_question,
                "language-id": language_id
            })
        
        logger.info(f"save Mongo Paylaod : {save_mongo_paylaod} ")

        # insert questions payload to MongoDB also save data in REdis for cahcing
        await chatbot_save_message_to_mongo_redis(db, master_collection, save_mongo_paylaod)

        # Prepare question entries for the SQL database
        question_entries = [
            {
                "current_question_key": idx + 1,
                "fields": f"question_answer_{message.question_key}",
                "msg_type": message.msg_type
            }
            for idx, message in enumerate(scr)
        ]

        #create question field map
        await create_question_field_map_dynamic_models(question_entries, ChatbotName, service_db_session)
        #create {chatbot}_detials table
        await create_dynamic_models(question_entries, ChatbotName)

    except Exception as e:
        logger.error(log_format(msg=f"Error in Insert Chatbot Conversation  : {e} "))
        return (str(e))

    else:
        return (save_mongo_paylaod)





@router.post("/chatbot/start_chatbot_conversation", summary="start_chatbot_conversation",
             status_code=status.HTTP_200_OK)
async def start_chatbot_conversation(request: Request, scr: Form = Depends(Payload),ChatbotName = str ,language_id: str = Header(1),
                                   image :List[UploadFile]=File(None) 
                                ):
    """
    Starts a conversation with the chatbot, processes messages based on the type (text, boolean, selection, image), 
    and saves dynamic responses in the database.

    - Retrieves the latest conversation message.
    - Handles different message types (text, boolean, multiple selection, single select, image).
    - Updates the database with responses and chatbot interactions.

    Args:
        request (Request): The incoming HTTP request.
        scr (Form): The payload containing the user's input data.
        ChatbotName (str): The name of the chatbot.
        language_id (str): The language ID (default is 1).
        image (List[UploadFile]): A list of uploaded image files.

    Returns:
        dict: A response containing the chatbot's next question or interaction.    """
    try:
        # language_id = int(request.headers.get('language-id', '1'))

        # Database credentials and sessions
        service_db_session, _ = await create_service_db_session()
        
        # MongoDB connection
        db ,_ , user_collection = create_mongo_connection()
        user_collection = f"{ChatbotName}{user_collection}"
        latest_message = db[user_collection].find_one(
            {"room_id": scr.room_id}, sort=[("created_at", DESCENDING)]
        )

        if scr.question_key == 1 :
            logger.info(f"Processing question with key: {scr.question_key}")
            msg_type  = get_msg_type_from_master_mongo(ChatbotName)
            logger.debug(f"Message type fetched from master MongoDB: {msg_type}")

            await conversation_operations(ChatbotName ,scr, db , user_collection, msg_type)

        elif scr.msg_type in [MsgType.Text.value, MsgType.Boolean.value , MsgType.MultipleSelect.value, MsgType.SingleSelect.value]:     #[1:text , 2:boolean , 3:multiple selection , 4:Single Select]
            #UPDATE THE RESPOSNE TO MONGO
            logger.info(f"Processing response with msg_type: {scr.msg_type}")

            if latest_message:
                update_latest_message(db, latest_message, scr.message, user_collection)
                logger.info(f"Updated latest message in MongoDB with message: {scr.message}")
            
            
            await conversation_operations(ChatbotName ,scr, db , user_collection, scr.msg_type)
           
        
        elif scr.msg_type == MsgType.Image:   #NOTE : dynamic logic still remaining for images
            if latest_message:
                if image:  # Raw image 
                    image_data =  image
                    image_url = update_latest_message_with_image(db, latest_message, image_data, user_collection)
                else:
                    update_latest_message(db, latest_message, scr.message, user_collection)

            ques = create_message(ChatbotName , scr, scr.question_key) #fetch the question details from master db(mongo) and create a dict 
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
                return user_details
            return None

        return construct_response(ChatbotName , scr, scr.question_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/chatbot/retrive_conversation", summary="dynamic chatbot conversation",
            status_code=status.HTTP_200_OK)
async def retrive_convsersation(ChatbotName  , request: Request, room_id :int ,language_id: str = Header(1)):
    room_list = get_question_data_from_room(ChatbotName , room_id)
    return room_list



#FETCH THE DETAILS FROM DB 
@router.get("/chatbot/get_question_paylaod_detail", summary="save_chatbot_conversation_db",
             status_code=status.HTTP_200_OK)
async def get_question_paylaod_detail(request: Request,language_id: str = Header(None)):
    """
    API to Insert Question paylaod
    """
    language_id = int(request.headers.get('language-id', '1'))
    try:  
        
        service_db_session,_ = await create_service_db_session()
        response_data = []
       
        question_respsone =  fetch_question_payload_query(service_db_session)
        response_data = [
            { "current_question_key": item.current_question_key,"fields": item.fields , "msg_type" : item.msg_type}
            for item in question_respsone
        ]
    except Exception as e:
        return (str(e))
    else:
        return response_data


