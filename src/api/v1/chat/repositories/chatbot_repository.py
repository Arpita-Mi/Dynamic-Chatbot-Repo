from sqlalchemy.orm import Session
from src.api.v1.chat.models.models import QuestionFieldsMap , UserResponse
from database.unit_of_work import SqlAlchemyUnitOfWork


async def get_question(db:Session, question_key : int):
    """    
    :param db: Description
    :type db: Session
    :param question_key: Description
    :type question_key: int
    :return: Description
    :rtype: Row[Tuple[int, str]] | Any | None
    """
    try:
        with SqlAlchemyUnitOfWork(db) as db:

            initial_question = db.query(
                QuestionFieldsMap.current_question_key,
                                        QuestionFieldsMap.fields
            ).filter(QuestionFieldsMap.current_question_key == question_key).first()
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
        with SqlAlchemyUnitOfWork(db) as db:
            question_key = question_data["message"]["question_key"]
        
            current_question_key = question_data.get("current_question_id") if question_key != 1 else question_key

            question_field_map = (
                db.query(QuestionFieldsMap)
                .filter(QuestionFieldsMap.current_question_key == current_question_key)
                .first()
            )

            if not question_field_map:
                raise Exception(f"No field mapping found for question_key {question_key}")

            field_name = question_field_map.fields

            previous_response = db.query(UserResponse).filter(UserResponse.id == question_data["id"]).first()

            if previous_response:
                setattr(previous_response, field_name, question_data.get("response"))
                db.flush()  
                db.commit()  
                db.refresh(previous_response) 
                return previous_response
            else:
                new_response = UserResponse(**{field_name: response.get("message")})
                db.add(new_response) 
                db.commit()  
                db.refresh(new_response) 
                return new_response

            

    except Exception as e:
        raise Exception("Something went wrong while saving the response.")