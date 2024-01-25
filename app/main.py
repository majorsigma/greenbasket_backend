"""The main entrypoint the greenbasket application"""
#pylint: disable=E0401, E0611

from fastapi import FastAPI
from app.routers import user_router
from app.utils import GBLogger

logger = GBLogger("main")
app = FastAPI()
app.include_router(user_router.router)

@app.get("/")
def read_root():
    """Greet the wold"""
    return {"message": "Welcome to GreenBasket"}
