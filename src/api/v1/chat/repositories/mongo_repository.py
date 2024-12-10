from pymongo.errors import ConnectionFailure, OperationFailure
from database.db_mongo_connect import MongoUnitOfWork

async def chatbot_update_data(db, collection_name: str, query: dict,update_values: dict):
    try:
        collection = db[collection_name]
        res = collection.update_one(query, {'$set': update_values})
        return res
    except (ConnectionFailure, OperationFailure) as e:
        raise Exception("Something went wrong")
    except Exception as e:
        raise Exception("Something went wrong")
    


async def insert_data(db, collection_name: str, data: dict):
    try:
        collection = db[collection_name]
        res = collection.insert_one(data)
        return res
    except (ConnectionFailure, OperationFailure) as e:
        raise Exception("Something went wrong")
    except Exception as e:
        raise Exception("Something went wrong")


def get_question_key_data(question_key):

    client, db = MongoUnitOfWork().mdb_connect()
    copilot_collection  = "demo_for_image" 
    question_data = db[copilot_collection].find_one({"message": {"$elemMatch": {"question_key": question_key }}},
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
