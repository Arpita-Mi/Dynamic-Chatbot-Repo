from pymongo import MongoClient
from config.config import settings


class MongoUnitOfWork:
    def mdb_connect(self, db_name=None, mongo_uri=None):
        """
        This Function return client and db after connect to Mongo server.
        :param db_name:
        :param mongo_uri:
        :return:
        """
        if not mongo_uri:
            mongo_uri = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASS}@{settings.MONGO_HOST}:{settings.MONGO_PORT}/"
        if not db_name:
            db_name = settings.MONGO_DB

        client = MongoClient(mongo_uri)
        db = client[db_name]
        return client, db
