from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://fastapi:1234@localhost/movie_db"
)

# Force pymysql driver even if URL starts with plain mysql://
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)


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
