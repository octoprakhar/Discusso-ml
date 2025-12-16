from fastapi import FastAPI
from app.api.routes import router
from app.utils.logger import setup_logger

setup_logger()

app = FastAPI(
    title="Discusso ML Service",
    version="0.1.0"
)

app.include_router(router=router)