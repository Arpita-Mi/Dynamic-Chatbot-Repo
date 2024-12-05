from fastapi import APIRouter
from src.api.v1.chat.views import chatbot_views
router = APIRouter(prefix="/api/v1")
 
router.include_router(chatbot_views.router)