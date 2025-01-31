from pymongo.errors import ConnectionFailure, OperationFailure
from database.db_mongo_connect import MongoUnitOfWork
from src.api.v1.chat.constants import constant
from database.db_mongo_connect import create_mongo_connection
from redis import Redis
import json
async def chatbot_update_data(db, master_collection: str, query: dict,update_values: dict):
    try:
        collection = db[master_collection]
        res = collection.update_one(query, {'$set': update_values})
        return res
    except (ConnectionFailure, OperationFailure) as e:
        raise Exception("Something went wrong")
    except Exception as e:
        raise Exception("Something went wrong")
    


async def insert_data(db, master_collection: str, data: dict):
    """
    Docstring for insert_data
    
    :param db: Description
    :type db: 
    :param master_collection: Description
    :type master_collection: str
    :param data: Description
    :type data: dict
    :return: Description
    :rtype: Any
    """
    try:
        collection = db[master_collection]
        res = collection.insert_one(data)
        return res
    except (ConnectionFailure, OperationFailure) as e:
        raise Exception("Something went wrong")
    except Exception as e:
        raise Exception("Something went wrong")


def get_question_key_data(ChatbotName ,question_key):
    """
    Docstring for get_question_key_data
    
    :param question_key: Description
    :type question_key: 
    :return: Description
    :rtype: Any | None
    """
    db ,master_collection , _ = create_mongo_connection()

    master_collection  =  f"{ChatbotName}{constant.MASTER_COLLECTION}"
    #Redis Connection
    redis_client = Redis(host="localhost", port=6379, db=0)
    redis_key = f"{master_collection}:message"


    # get the data from redis cahcing 
    cached_room_id = redis_client.get(redis_key)
    if cached_room_id:
        parsed_data = json.loads(cached_room_id)

        message_data = parsed_data.get("message" , [])

        wrapped_msg = {"message" : [msg for msg in message_data if msg.get("question_key") == question_key]}
        if wrapped_msg:
            return wrapped_msg

    
    
    #if data not found in redis fetch it from mongo
    question_data = db[master_collection].find_one({"message": {"$elemMatch": {"question_key": question_key }}},
                            {"message.$": 1, "_id": 0})
    return question_data

async def update_data(db, user_collection: str, query: dict, update_values: dict):
    try:
        collection = db[user_collection]
        res = collection.update_one(query, {'$set': update_values})
        return res
    except Exception as e:
        raise e
    except Exception as e:
        raise e

