from fastapi import FastAPI
from src.route.router import router


app = FastAPI()


app.include_router(router)
