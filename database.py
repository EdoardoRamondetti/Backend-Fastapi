from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

with engine.connect() as connection:
    print("Database connected!")

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()