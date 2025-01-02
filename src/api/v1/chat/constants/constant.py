from enum import Enum
from sqlalchemy import String , Integer , Boolean , JSON , Float
MASTER_COLLECTION = "_chatbot"
USER_COLLECTION = "_conversation_data"
IMAGE_BASE_URL =  "https://example.com/images"
STATIC_MODEL_PATH = "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/src/api/v1/chat/models/static_model.py"
DYNAMIC_MODEL_PATH = "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/src/api/v1/chat/models/dynamic_models"
ALEMBIC_INI_PATH =  "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/alembic.ini"
QUESTION_FIELD_MAP_MODEL_PATH =  "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/src/api/v1/chat/models/question_filed_map_static.py"
DYNAMIC_QUESTION_FIELD_MAP_MODEL_PATH =  "/home/mind/Dynamic-Chatbot-Repo-Git-Hub/src/api/v1/chat/models/dynamic_question_map_filed"


class MsgType(Enum):
    String = 1
    Boolean = 2
    JSON = 3

value_to_type = {
    1:MsgType.String,
    2:MsgType.Boolean,
    3:MsgType.JSON,
    4:MsgType.JSON,
    5:MsgType.String
}


#Implemented MSG TYPES                  # TOTAL TYPES
#1. String/Text                         # 0,  Error
#2. Boolean                             #  1,  Message,
#3. Multiple Select                     # 2,  bool,
#4. Single Select                       # 4,  skip,
#5. Images                              # 5,  location,
                                        # 6,  images,
                                        # 3,  single options,
                                        # 7,  multiple selection,
                                        # 8,  checklist,
                                        # 9,  user_message,
                                        # 10, end_flow,
                                        # 11, skip_with_groupchat,
                                        # 12, input_project,
                                        # 13, View form detail,
                                        # 14, Reviewer Name,
                                        # 15, attendees,
                                        # 16, statistic_form,
                                        # 17, exit-button,
                                        # 18, calendar,