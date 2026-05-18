from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import heroes, auth, missions
from app.db import engine

settings = get_settings()


# --- Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


# --- App Instance ---

app = FastAPI(title="Heroes App",
              description="A FastAPI app that handles heroes missions.",
              version="1.0.0",
              lifespan=lifespan,
              )

# --- Middleware ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# --- Routers ---

app.include_router(auth.router)
app.include_router(heroes.router)
app.include_router(missions.router)


# --- Root ---

@app.get("/", tags=["root"])
def root():
    """Health check / welcome endpoint."""
    return {"message": "FastAPI Heroes App", "docs": "/docs"}
