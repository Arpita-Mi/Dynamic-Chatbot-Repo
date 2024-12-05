from database.database_manager import DatabaseManager
async def get_service_db_session(service_db_credentials: dict): 
    session, _ = DatabaseManager(
        username=service_db_credentials["username"],
        password=service_db_credentials["password"],
        hostname=service_db_credentials["hostname"],
        port=service_db_credentials["port"],
        db_name=service_db_credentials["db_name"]).service_db_session()
    return session