from src.api.v1.chat.repositories.chatbot_repository import get_question,save_user_response
from src.api.v1.chat.schemas.schema import Payload
from src.api.v1.chat.services.mongo_services import fetch_question_data_from_mongo
from database.db_mongo_connect import MongoUnitOfWork
from src.api.v1.chat.constants import constant
from datetime import datetime
import os
import shutil

async def get_question_field_map_resposne(question_key :int , service_db_session = None):
    """
    Docstring for get_question_field_map_resposne
    
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
    Docstring for save_respose_db
    
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
    Docstring for create_message
    
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
    Docstring for update_latest_message
    
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
    Docstring for update_latest_message_with_image
    
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
    Docstring for construct_response
    
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


def create_dynamic_models(question_entries, Organization_Name):
        # File handling logic to create a new file and copy static_model.py content
        static_model_path = "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/src/api/v1/chat/models/static_model.py" 
        dynamic_model_path = "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/src/api/v1/chat/models/dynamic_models"
        new_file_path = f"{dynamic_model_path}/{Organization_Name}_model.py"
        replace_table_and_class_name(static_model_path, dynamic_model_path, Organization_Name)

        # if not os.path.exists(dynamic_model_path):
        #     os.makedirs(dynamic_model_path)
            
        # shutil.copy(static_model_path, new_file_path)

        
        with open(new_file_path, "a+") as f:
            for qes in question_entries:
                dynamic_field = qes["fields"]
                msg_type_column = qes["msg_type"]
                if msg_type_column == 3:
                    msg_column = constant.value_to_type[msg_type_column].name.upper()
                else:
                    msg_column = constant.value_to_type[msg_type_column].name.capitalize()
                f.write(f"\n    {dynamic_field} = Column({msg_column})")
                f.seek(0)
                print(f.read())


            

def replace_table_and_class_name(static_model_path, dynamic_model_path, organization_name):
    # Define the new file path
    new_file_path = f"{dynamic_model_path}/{organization_name}_model.py"
    
    # Ensure the directory exists
    if not os.path.exists(dynamic_model_path):
        os.makedirs(dynamic_model_path)
    
    # Read the content of the static model file
    with open(static_model_path, 'r') as file:
        content = file.read()
    
    # Replace the table name and class name
    new_table_name = f"{organization_name.lower()}_details"
    new_class_name = f"{organization_name.capitalize()}Details"
    content = content.replace("__tablename__ = 'incident_details'", f"__tablename__ = '{new_table_name}'")
    content = content.replace("class IncidentDetails(Base):", f"class {new_class_name}(Base):")
    
    # Write the updated content to the new file
    with open(new_file_path, 'w') as file:
        file.write(content)
    
    print(f"File successfully created at: {new_file_path}")



        

