import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DB_DIR = "data"
os.makedirs(DB_DIR, exist_ok=True)
sqlite_url = f"sqlite:///{DB_DIR}/database.db"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session