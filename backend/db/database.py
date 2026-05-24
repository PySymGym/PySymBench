import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


def get_db_url() -> str:
    url = os.getenv("DB_URL")
    if not url:
        raise RuntimeError("Environment variable DB_URL is not set")
    return url


engine = create_engine(get_db_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
