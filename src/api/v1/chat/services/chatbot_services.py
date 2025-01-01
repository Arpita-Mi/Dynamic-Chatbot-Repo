from src.api.v1.chat.repositories.chatbot_repository import get_question,save_user_response
from src.api.v1.chat.schemas.schema import Payload
from src.api.v1.chat.services.mongo_services import fetch_question_data_from_mongo
from database.db_mongo_connect import MongoUnitOfWork
from src.api.v1.chat.constants import constant
from datetime import datetime
from database.db_connection import create_service_db_session
from sqlalchemy import Integer , String, MetaData , Column , Boolean , JSON
from database.database_manager import Base
from src.api.v1.chat.models.question_filed_map_static import dynamic_question_filed_map
from src.api.v1.chat.repositories.chatbot_repository import save_question_payload_query
from sqlalchemy.orm import Session
import os
import shutil
from logger.logger import logger , log_format


async def get_question_field_map_resposne(question_key :int , service_db_session = None):
    """
    get_question_field_map_resposne
    
    :param question_key: Description
    :type question_key: int
    :param service_db_session: Description
    :type service_db_session: 
    :return: Description
    :rtype: dict[str, Any]
    """
    initial_question = await get_question(service_db_session ,question_key)
    message = {
        "question_key" : initial_question.current_question_key,
        "fields": initial_question.fields,
        
    }
    return message

async def save_respose_db(question_data : dict , response :dict,service_db_session = None):
    """
    save_respose_db
    
    :param question_data: Description
    :type question_data: dict
    :param response: Description
    :type response: dict
    :param service_db_session: Description
    :type service_db_session: 
    :return: Description
    :rtype: dict[str, Column[int] | Any]
    """
   
    initial_question = await save_user_response(service_db_session ,question_data,response)
    initial_question = {"id" : initial_question.id,
                        # "question_key" : question_data["question_key"],
                        # "msg_text" : question_data["msg_text"],
                        # "msg_type" :question_data["msg_type"],
                        # "next_question" :question_data["next_question"],
                        # "language-id" : question_data["language-id"] 
                        }
    return initial_question



def create_message(scr: Payload, question_key: int) -> dict:
    """
    create_message
    
    :param scr: Description
    :type scr: Payload
    :param question_key: Description
    :type question_key: int
    :return: Description
    :rtype: Any
    """
    time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return {
        "room_id": scr.room_id,
        "sender_id": scr.sender_id,
        "message": fetch_question_data_from_mongo(question_key=question_key),
        "created_at": time_now
    }


def update_latest_message( db,  latest_message, response_message, user_collection) -> None:
    """
    update_latest_message
    
    :param db: Description
    :type db: 
    :param latest_message: Description
    :type latest_message: 
    :param response_message: Description
    :type response_message: 
    :param user_collection: Description
    :type user_collection: 
    :return: Description
    :rtype: Any
    """
    time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    update_values = {
        "message.response": response_message,
        "message.response_time": time_now
    }
    db[user_collection].update_one(
        {"_id": latest_message["_id"]}, {"$set": update_values}
    )

def update_latest_message_with_image(db,  latest_message, image_data, user_collection):
    """
    update_latest_message_with_image
    
    :param db: Description
    :type db: 
    :param latest_message: Description
    :type latest_message: 
    :param image_data: Description
    :type image_data: 
    :param user_collection: Description
    :type user_collection: 
    :return: Description
    :rtype: str
    """
    time_now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    update_list = []
    image_list = generate_image_url(image_data)
    for i in image_list:
      
        update_list.append( i["image_url"])
   
    db[user_collection].update_one(
        {"_id": latest_message["_id"]}, {"$set": {"message.response"  : update_list , "message.response_time" : time_now} }
    )
    return image_list




def construct_response(scr: Payload, question_key: int) -> dict:
    """
    construct_response
    
    :param scr: Description
    :type scr: Payload
    :param question_key: Description
    :type question_key: int
    :return: Description
    :rtype: Any
    """
    return {
        "room_id": scr.room_id,
        "sender_id": scr.sender_id,
        "message": fetch_question_data_from_mongo(
            question_key=question_key
        )
    }



def generate_image_url(image_data) -> str:
    """
    Generate an image name and URL for the uploaded image.
    """
    image_list = []
    base_url = constant.IMAGE_BASE_URL
    for img_data in image_data:
        extension = (img_data.filename)  
        image_name = f"{extension}"
        image_url = f"{base_url}/{image_name}"
        image_list.append({"image_name" : image_name, "image_url" : image_url})
    return image_list



def get_question_data_from_room(room_id):
    """ 
    :param room_id: Description
    :type room_id: 
    :return: Description
    :rtype: list
    """
    client, db = MongoUnitOfWork().mdb_connect()
    user_collection  =  constant.USER_COLLECTION
    room_data = db[user_collection].find({"room_id": room_id },
                            {"room_id":0 ,"_id": 0})
    room_list = list(room_data)
    return room_list


    

async def create_dynamic_models(question_entries, ChatbotName):
    try:
        # Logging the initial API call
        logger.info(log_format(msg="Initial API call to create dynamic models"))

        # Create a service DB session and engine
        _, engine = await create_service_db_session()

        # Initialize fields dictionary
        fields = {}

        # Table name based on ChatbotName
        table_name = f"{ChatbotName}_details"
        logger.info(f"Table name generated: {table_name}")

        for entry in question_entries:
            field = entry['fields']
            msg_type = entry['msg_type']
            
            logger.debug(f"Processing field: {field} with message type: {msg_type}")

            # Map msg_type to SQLAlchemy column type dynamically
            column_type = msg_type_to_column(msg_type)

            if column_type:
                fields[field] = column_type
            else:
                logger.warning(f"Invalid message type '{msg_type}' for field '{field}'")

        # Dynamically generate the model based on the table and fields
        DynamicModel = dynamic_question_filed_map(table_name, fields)
        logger.info(f"Dynamic {table_name}_details generated")

        # Create the table in the database
        Base.metadata.create_all(engine)
        logger.info(f"Table {table_name} created successfully.")

    except Exception as e:
        logger.error(f"Error while creating dynamic models for {ChatbotName}: {str(e)}")
        raise



async def create_question_field_map_dynamic_models(question_entries, chatbot_name, db: Session):
    """
    Dynamically creates the QuestionFieldsMap table if it doesn't exist and inserts data.
    """
    try:
        # Log the start of the API call
        logger.info(log_format(msg="Initial API call to create QuestionFieldMap dynamic model"))

        # Create a service DB session and engine
        service_db_session, engine = await create_service_db_session()

        # Define table name dynamically
        table_name = f"{chatbot_name}_question_field_map"
        logger.info(f"Table name generated: {table_name}")

        # Define fields for the dynamic model
        fields = {
            "current_question_key": Integer,
            "fields": String,
            "msg_type": String,
        }

        # Create dynamic model
        DynamicTable = dynamic_question_filed_map(table_name, fields)
        logger.info(f"Dynamic model created for table: {table_name}")

        # Ensure the table is created in the database
        Base.metadata.create_all(engine)
        logger.info(f"Table {table_name} created successfully in the database.")

        # Save the question entries using the dynamic model
        await save_question_payload_query(service_db_session, question_entries, DynamicTable)
        logger.info(f"Question entries successfully inserted into {table_name}.")

    except Exception as e:
        logger.error(f"Error while creating dynamic model for QuestionFieldMap in {chatbot_name}: {str(e)}")
        raise

  

def msg_type_to_column(msg_type):
    if msg_type == constant.MsgType.String.value:
        return String
    elif msg_type == constant.MsgType.Boolean.value:
        return Boolean
    elif msg_type == constant.MsgType.JSON.value:
        return JSON
    else:
        return String 

def clear_pycache():
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))



from sqlalchemy import inspect

def get_chatbot_tables(engine, pattern="_question_field_map"):
    """
    Fetch all dynamic chatbot table names matching the pattern.
    """
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    # Filter tables based on the naming convention
    chatbot_tables = [table for table in all_tables if table.endswith(pattern)]
    return chatbot_tables



from sqlalchemy import Table, MetaData
from sqlalchemy.orm import Session

def fetch_table_data(engine, table_name):
    """
    Fetch data from a dynamically created table.
    """
    metadata = MetaData()
    # Reflect the table structure
    table = Table(table_name, metadata, autoload_with=engine)
    
    with Session(engine) as session:
        # Query the table
        query = session.query(table)
        results = query.all()
        return [dict(row._mapping) for row in results]


async def fetch_chatbot_table_details(chatbot_name):
    """
    Fetch details of the dynamic chatbot tables.
    """
    # Create a service DB session and engine
    service_db_session, engine = await create_service_db_session()

    # Fetch all chatbot-related tables
    chatbot_tables = get_chatbot_tables(engine)
    logger.info(f"Found chatbot tables: {chatbot_tables}")

    chatbot_data = {}
    for table_name in chatbot_tables:
        if chatbot_name in table_name:  # Filter tables for the specific chatbot
            data = fetch_table_data(engine, table_name)
            chatbot_data[table_name] = data

            return chatbot_data , table_name
