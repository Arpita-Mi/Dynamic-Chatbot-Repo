from enum import Enum

MASTER_COLLECTION = "demo"
USER_COLLECTION = "user_data"
IMAGE_BASE_URL =  "https://example.com/images"


class MsgType(Enum):
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"

value_to_type = {
    1: MsgType.STRING,
    2:MsgType.BOOLEAN,
    3:MsgType.JSON,
    4:MsgType.JSON,
    5:MsgType.STRING
}
  




# 0,  Error
# 1,  Message,
# 2,  bool,
# 4,  skip,
# 5,  location,
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