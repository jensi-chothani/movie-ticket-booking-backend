from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://fastapi:1234@localhost/movie_db"
)


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()