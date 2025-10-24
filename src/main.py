import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from src.db.manager import sessionmanager
from src.force_stop.router import router as force_stop_router
from src.normal_document.router import router as normal_document_router
from src.auth.dependency import get_api_key
from src.app_logger.manager import setup_logging


logger = logging.getLogger(__name__)
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):

    yield
    if sessionmanager._engine is not None:
        sessionmanager.close()


app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_api_key)])

app.include_router(normal_document_router)
app.include_router(force_stop_router)
