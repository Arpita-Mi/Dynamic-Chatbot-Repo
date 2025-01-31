from src.api.v1.chat.repositories.mongo_repository import insert_data, chatbot_update_data , get_question_key_data , update_data
from bson import ObjectId
from logger.logger import logger , log_format
from src.api.v1.chat.schemas.schema import Payload
from src.api.v1.chat.constants import constant
from database.db_mongo_connect import create_mongo_connection
from datetime import datetime
from redis import Redis
import json

async def chatbot_save_message_to_mongo_redis(db, master_collection,  message: str):
    """
    Insert Message Payload to redis for chaching use
    Insert Message after checking and deleting existing data.
    :param db: MongoDB database connection
    :param master_collection: MongoDB collection name
    :param message: List of messages to insert
    :param language_id: Language ID to check for existing data
    :return:
    """

    existing_data = db[master_collection].find({})  
    logger.info(log_format(msg = "Check if data already exists for the given language_id"))
    if existing_data:
        logger.info(log_format(msg="Existing document found with _id  deleting..."))
        delete_result = db[master_collection].delete_many({})
        logger.info(log_format(msg=f"Deleted {delete_result.deleted_count} records from {master_collection}"))

    logger.info(log_format(msg=f"Inserting new data for message {message}"))
    data = {
        "message": message,
    }
    res = await insert_data(db, master_collection, data)
    logger.info(log_format(msg=f"Inserted ({res.inserted_id}) records"))

    # Handling Redis Process
    redis_client = Redis(host="localhost", port=6379, db=0)
    redis_key = f"{master_collection}:message"
    #Serialize the resposne for redis storage 
    json_data =  make_serializable(data)
    redis_client.set(redis_key , json.dumps(json_data))
    logger.info(log_format(msg=f"save question paylaod in redis Key : {redis_key} , questions : {json.dumps(json_data)}"))
    return res.inserted_id


def make_serializable(data):
    if isinstance(data, dict):
        return {key: make_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [make_serializable(item) for item in data]
    elif isinstance(data, ObjectId): 
        return str(data)
    elif isinstance(data, datetime):  
        return data.isoformat()
    return data



async def chatbot_update_message(db, master_collection, message_id: str, current_question_id : int, update_values: dict):
    """
    Update Message
    :param db:
    :param master_collection:
    :param message_id:
    :param update_values:
    :return:
    """
    query = {"message": {"$elemMatch": {"question_key": current_question_id }}, "_id" : ObjectId(message_id) }
    res = await chatbot_update_data(db, master_collection, query , update_values)
    return res


def fetch_question_data_from_mongo(ChatbotName , question_key):
    """    
    :param question_key: Description
    :type question_key: 
    :return: Description
    :rtype: Any | None
    """
    question_data = get_question_key_data(ChatbotName , question_key)
    if question_data:
        list_question = question_data.get("message")
        ques = list_question[0]
        return ques

# def fetch_question_data_from_redis()


async def update_message(db, user_collection, current_question_id, update_values: dict):
    """
    Update Message
    :param db:
    :param master_collection:
    :param current_question_id:
    :param update_values:
    :return:
    """
    query = {"message.question_key" : current_question_id }
    res = await update_data(db, user_collection, query, update_values)
    return res



def create_message(ChatbotName , scr: Payload, question_key: int) -> dict:
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
        "message": fetch_question_data_from_mongo(ChatbotName , question_key=question_key),
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




def construct_response(ChatbotName ,scr: Payload, question_key: int) -> dict:
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
        "message": fetch_question_data_from_mongo(ChatbotName,
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


def get_question_data_from_room(ChatbotName, room_id):
    """ 
    :param room_id: Description
    :type room_id: 
    :return: Description
    :rtype: list
    """
    db, _, user_collection = create_mongo_connection()
    room_data = db[user_collection].find({"room_id": room_id},
                                         {"room_id": 0, "_id": 0})
    room_list = list(room_data)
    return room_list


def get_msg_type_from_master_mongo(ChatbotName):

    db, master_collection, _ = create_mongo_connection()
    master_collection = f"{ChatbotName}{master_collection}"
    master_data = db[master_collection].find({})
    # print(list(master_data))
    for record in master_data:
        for message in record.get('message', []):
            if message.get('question_key') == 1:
                print("msg_type:", message.get('msg_type'))
                return message.get('msg_type')
