from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)