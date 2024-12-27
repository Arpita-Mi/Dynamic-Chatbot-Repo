from src.api.v1.chat.repositories.mongo_repository import insert_data, chatbot_update_data , get_question_key_data , update_data
from bson import ObjectId
from logger.logger import logger , log_format


async def chatbot_insert_message(db, collection_name,  message: str):
    """
    Insert Message after checking and deleting existing data.
    :param db: MongoDB database connection
    :param collection_name: MongoDB collection name
    :param message: List of messages to insert
    :param language_id: Language ID to check for existing data
    :return:
    """
    # Check if data already exists for the given language_id
    existing_data = db[collection_name].find({})  # Query with an empty filter to find any document
    if existing_data:
        logger.info(log_format(msg="Existing document found with _id  deleting..."))
        # Delete all documents in the collection
        delete_result = db[collection_name].delete_many({})
        logger.info(log_format(msg=f"Deleted {delete_result.deleted_count} records from {collection_name}"))

    # Insert the new data
    logger.info(log_format(msg=f"Inserting new data for message {message}"))
    data = {
        "message": message,
    }
    res = await insert_data(db, collection_name, data)
    
    logger.info(log_format(msg=f"Inserted ({res.inserted_id}) records"))
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