# core/database.py
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# 確保 data 資料夾存在
os.makedirs("data", exist_ok=True)

# 將資料庫路徑改為 data/database.db
sqlite_url = "sqlite:///data/database.db"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session