"""The main entrypoint the greenbasket application"""
from fastapi import FastAPI
# from app.dependencies import UnitOfWork
from app.utils import GBLogger
from app.routers import user_router

logger = GBLogger("main")
app = FastAPI()
app.include_router(user_router.router)

@app.get("/")
def read_root():
    """Greet the wold"""
    # uow = UnitOfWork()
    return {"message": "Welcome to GreenBasket"}