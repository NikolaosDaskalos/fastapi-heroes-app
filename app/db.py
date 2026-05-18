from sqlmodel import create_engine, SQLModel, Session
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a database session per request."""
    with Session(engine) as session:
        yield session
