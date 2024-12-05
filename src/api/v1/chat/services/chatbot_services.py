from src.api.v1.chat.repositories.chatbot_repository import get_question,save_user_response


async def get_question_field_map_resposne(question_key :int , service_db_session = None):
    initial_question = await get_question(service_db_session ,question_key)
    message = {
        "question_key" : initial_question.current_question_key,
        "fields": initial_question.fields,
        
    }
    return message

async def save_respose_db(question_data : dict , response :dict,service_db_session = None):
    initial_question = await save_user_response(service_db_session ,question_data,response)
    # for initial_question in initial_questions:
    initial_question = {"id" : initial_question.id,
                        "question_key" : question_data["question_key"],
                        "msg_text" : question_data["msg_text"],
                        "msg_type" :question_data["msg_type"],
                        "next_question" :question_data["next_question"],
                        "language-id" : question_data["language-id"] }
    return initial_question


