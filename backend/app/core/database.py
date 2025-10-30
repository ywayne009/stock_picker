"""Database Connection"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def get_db():
    db = None
    try:
        yield db
    finally:
        if db:
            db.close()
