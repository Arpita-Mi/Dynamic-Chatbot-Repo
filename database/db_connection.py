from database.database_manager import DatabaseManager
from config.config import settings
async def get_service_db_session(service_db_credentials: dict): 
    session, _ = DatabaseManager(
        username=service_db_credentials["username"],
        password=service_db_credentials["password"],
        hostname=service_db_credentials["hostname"],
        port=service_db_credentials["port"],
        db_name=service_db_credentials["db_name"]).service_db_session()
    return session


async def create_service_db_session():
    service_db_credentials = {
            "username": settings.SERVICE_DB_USER,
            "password": settings.SERVICE_DB_PASSWORD,
            "hostname": settings.SERVICE_DB_HOSTNAME,
            "port": settings.SERVICE_DB_PORT,
            "db_name": settings.SERVICE_DB
        }
    service_db_session = await get_service_db_session(service_db_credentials)
    return service_db_session