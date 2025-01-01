from src.api.v1.chat.repositories.chatbot_repository import get_question,save_user_response
from src.api.v1.chat.constants import constant
from database.db_connection import create_service_db_session
from sqlalchemy import Integer , String, MetaData , Column , Boolean , JSON
from database.database_manager import Base
from src.api.v1.chat.models.question_filed_map_static import dynamic_question_filed_map
from src.api.v1.chat.repositories.chatbot_repository import save_question_payload_query
from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData
from sqlalchemy.orm import Session
from sqlalchemy import inspect
import os
import shutil
from logger.logger import logger , log_format


async def get_question_field_map_resposne(table_name : str ,question_key :int , service_db_session = None):
    """
    get_question_field_map_resposne
    
    :param question_key: Description
    :type question_key: int
    :param service_db_session: Description
    :type service_db_session: 
    :return: Description
    :rtype: dict[str, Any]
    """
    initial_question = await get_question(table_name ,service_db_session ,question_key)
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


async def fetch_chatbot_table_details(chatbot_name):
    """
    Fetch details of the dynamic chatbot tables.
    """
    # Create a service DB session and engine
    service_db_session, engine = await create_service_db_session()

    # Fetch all chatbot-related tables
    patterns = ["_question_field_map", "_details"]
    chatbot_tables = get_chatbot_tables(engine,chatbot_name , patterns)
    logger.info(f"Found chatbot tables: {chatbot_tables}")

    chatbot_data = {}
    for table_name in chatbot_tables:
        if chatbot_name in table_name:  # Filter tables for the specific chatbot
            data = fetch_table_data(engine, table_name)
            chatbot_data[table_name] = data

            return chatbot_data , chatbot_tables

  

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





def get_chatbot_tables(engine, chatbot_name , patterns=None):
    """
    Fetch all dynamic chatbot table names matching the pattern.
    """
    if patterns is None:
        patterns = ["_question_field_map", "_details"]
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    # Filter tables based on the naming convention
    chatbot_tables = [table
        for table in all_tables
        if chatbot_name in table and any(pattern in table for pattern in patterns)]
    return chatbot_tables




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


