from sqlalchemy.orm import Session
from sqlalchemy import Table , MetaData
from src.api.v1.chat.models.models import QuestionFieldsMap , UserResponse
from database.db_connection import create_service_db_session
from database.unit_of_work import SqlAlchemyUnitOfWork
from logger.logger import logger , log_format
from alembic import command
from alembic.config import Config
from src.api.v1.chat.constants import constant
from types import SimpleNamespace

async def get_question(table_name , db:Session, question_key : int):
    """    
    :param db: Description
    :type db: Session
    :param question_key: Description
    :type question_key: int
    :return: Description
    :rtype: Row[Tuple[int, str]] | Any | None
    """
    try:
        _, engine = await create_service_db_session()
        metadata =  MetaData()
        with SqlAlchemyUnitOfWork(db) as db:
            dynamci_tables =  Table(table_name, metadata , autoload_with=engine)
            initial_question = db.query(
                dynamci_tables.c.current_question_key,
                                        dynamci_tables.c.fields
            ).filter(dynamci_tables.c.current_question_key == question_key).first()
    except Exception as e:
        raise Exception("Something went wrong")
    else:
        return initial_question
    
   


async def save_user_response(db: Session, question_data: dict, response: dict):
    """    
    :param db: Description
    :type db: Session
    :param question_data: Description
    :type question_data: dict
    :param response: Description
    :type response: dict
    :return: Description
    :rtype: UserResponse | Any
    """
    try:
        # with SqlAlchemyUnitOfWork(db) as db:
        #     question_key = question_data["message"]["question_key"]
        
        #     current_question_key = question_data.get("current_question_id") if question_key != 1 else question_key
        #     if question_key == 2 and current_question_key == 1:
        #         return SimpleNamespace(id=question_key)  #returns object with attributes dynamically
        #     question_field_map = (
        #         db.query(QuestionFieldsMap)
        #         .filter(QuestionFieldsMap.current_question_key == current_question_key)
        #         .first()
        #     )

        #     if not question_field_map:
        #         raise Exception(f"No field mapping found for question_key {question_key}")

        #     field_name = question_field_map.fields

        #     previous_response = db.query(UserResponse).filter(UserResponse.id == question_data["id"]).first()
        #     #Update the Resposne field
        #     if previous_response:
        #         setattr(previous_response, field_name, question_data.get("response"))
        #         db.flush()  
        #         db.commit()  
        #         db.refresh(previous_response) 
        #         return previous_response
        #     else:
        #         if question_key == 1:
        #             # Create a new response with null message for question_key == 1
        #             new_response = UserResponse(**{field_name: None})
        #         else:
        #             # Create a new response with the provided message
        #             new_response = UserResponse(**{field_name: question_data.get("message")})
        #         # new_response = UserResponse(**{field_name: response.get("message")})
        #         db.add(new_response) 
        #         db.commit()  
        #         db.refresh(new_response) 
        #         return new_response
        pass
            

    except Exception as e:
        raise Exception("Something went wrong while saving the response.")
    
async def save_respose_dynamic_db(msg_type , question_field_map_table:str , details_table: str , question_data : dict , response :dict,service_db_session = None):
    """
    save_respose_db
    """
   
    initial_question = await save_dynamic_user_response(msg_type,question_field_map_table , details_table,service_db_session ,question_data,response)
    initial_question = {"id" : initial_question.id  }
    return initial_question



async def save_dynamic_user_response(msg_type,question_field_map_table ,details_table, db: Session, question_data: dict, response: dict):
    """    
    :param db: Description
    :type db: Session
    :param question_data: Description
    :type question_data: dict
    :param response: Description
    :type response: dict
    :return: Description
    :rtype: UserResponse | Any
    """
    try:
        with SqlAlchemyUnitOfWork(db) as db:
            metadata = MetaData()
            
            dynamic_question_map_table = Table(question_field_map_table, metadata, autoload_with=db.bind)
            dynamic_details_table = Table(details_table, metadata, autoload_with=db.bind)
            logger.info(log_format(msg=f"loads tables dynamically from db {dynamic_question_map_table} and {dynamic_details_table}"))


            question_key = question_data["message"]["question_key"]
            current_question_key = question_data.get("current_question_id") if question_key != 1 else question_key
            logger.info(log_format(msg=f"Extract Question Keys : {current_question_key}"))

            try:
                question_field_map = (
                    db.query(dynamic_question_map_table)
                    .filter(dynamic_question_map_table.c.current_question_key == current_question_key)
                    .first()
                )
                logger.info(log_format(msg=f"Fetch the qustion filed map {question_field_map}"))

                # if not question_field_map:
                #     logger.error(log_format(msg=f"no field mapping found for question_key : {question_key}"))
                #     raise Exception(f"No field mapping found for question_key {question_key}")

                field_name = question_field_map.fields
            except ValueError as e:
                logger.error(log_format(msg=f" ERROR : {e}"))

            # Handle specific cases for question_key and msg_type
            if  (
                    (question_key == 2 and current_question_key == 1 and msg_type == constant.MsgType.Boolean.value) or 
                    (question_key == 1 and msg_type != constant.MsgType.Boolean.value)
                ):
                new_row_data = {field_name: None}
                db.execute(dynamic_details_table.insert().values(**new_row_data))
                db.commit()
                return db.query(dynamic_details_table).order_by(dynamic_details_table.c.id.desc()).first()

            # Fetch previous response
            previous_response = (
                db.query(dynamic_details_table)
                .filter(dynamic_details_table.c.id == question_data["id"])
                .first()
            )

            if previous_response:
                logger.info(log_format(msg=f"Previous response found, Previous_Response : {previous_response}"))
                update_stmt = (
                    dynamic_details_table.update()
                    .where(dynamic_details_table.c.id == previous_response.id)
                    .values({field_name: question_data.get("response")})
                )
                db.execute(update_stmt)
                db.commit()
                return db.query(dynamic_details_table).filter(dynamic_details_table.c.id == previous_response.id).first()
            logger.warning(log_format(msg=f"No Previous Response Found , Previous_Response :  {previous_response}"))

            # Default case
            return SimpleNamespace(id=question_key)

    except Exception as e:
        raise Exception("Something went wrong while saving the response.") from e




async def save_question_payload_query(db: Session, question_entries,DynamicTable):
    """
    Saves question data into the QuestionFieldsMap table with a prefix for the fields column.
    The current_question_key is incremented for each entry.
    """
    try:
        with SqlAlchemyUnitOfWork(db) as db:
            for question_entry in question_entries:
                record = DynamicTable(
                        current_question_key=question_entry["current_question_key"],
                        fields=question_entry["fields"],
                        msg_type=question_entry["msg_type"],
                    )
                        
                db.add(record)
                db.flush()  
                db.commit() 
    except Exception as e:
        await db.rollback()
        raise Exception(f"Error saving question data: {e}")

def fetch_question_payload_query(db:Session):
    try:
        with SqlAlchemyUnitOfWork(db) as db:
            question_resposne = db.query(QuestionFieldsMap).all()
    except Exception as e:
        raise Exception(f"Error saving question data: {e}")
    else:
        return question_resposne
        

    
def run_alembic_migration():
    try:
        alembic_cfg = Config(constant.ALEMBIC_INI_PATH)
        command.revision(alembic_cfg, message="Dynamic model update", autogenerate=True)
        command.upgrade(alembic_cfg, "head")
        logger.info(log_format(msg="run_alembic_migrations"))
    except Exception as e:
        logger.error(log_format(msg=f"Error during Alembic migration : {e}"))