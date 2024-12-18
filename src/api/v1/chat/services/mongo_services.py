from src.api.v1.chat.repositories.mongo_repository import insert_data, chatbot_update_data , get_question_key_data , update_data
from bson import ObjectId
async def chatbot_insert_message(db, collection_name,  message: str):
    """
    Insert Message
    :param db:
    :param collection_name:
    :param message:
    :return:
    """
    data = {
        "message": message,
    }
    res = await insert_data(db, collection_name, data)
    return res.inserted_id


async def chatbot_update_message(db, collection_name, message_id: str, current_question_id : int, update_values: dict):
    """
    Update Message
    :param db:
    :param collection_name:
    :param message_id:
    :param update_values:
    :return:
    """
    query = {"message": {"$elemMatch": {"question_key": current_question_id }}, "_id" : ObjectId(message_id) }
    res = await chatbot_update_data(db, collection_name, query , update_values)
    return res


def fetch_question_data_from_mongo(question_key):
    """    
    :param question_key: Description
    :type question_key: 
    :return: Description
    :rtype: Any | None
    """
    question_data = get_question_key_data(question_key)
    if question_data:
        list_question = question_data.get("message")
        ques = list_question[0]
        return ques



async def update_message(db, user_collection, current_question_id, update_values: dict):
    """
    Update Message
    :param db:
    :param collection_name:
    :param current_question_id:
    :param update_values:
    :return:
    """
    query = {"message.question_key" : current_question_id }
    res = await update_data(db, user_collection, query, update_values)
    return res