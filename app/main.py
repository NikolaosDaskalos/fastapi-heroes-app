from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Heroes App", lifespan=lifespan)