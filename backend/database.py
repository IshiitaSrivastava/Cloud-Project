# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.config import Config

connect_args = {}
# sqlite needs check_same_thread flag when used in multi-threaded environment (Flask dev)
if Config.SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, connect_args=connect_args)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
