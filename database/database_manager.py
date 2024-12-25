import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.pool import NullPool



# Declare the database ORM class
Base = declarative_base()


class DatabaseManager:
    """
    Create database Engine and Session
    """
    def __init__(self, username: str, password: str, hostname: str, port: str, db_name: str):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port
        self.db_name = db_name

    def database_url(self):
        DATABASE_URL = f"postgresql+psycopg2://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.db_name}"
        return DATABASE_URL

    def service_db_session(self):
        engine = create_engine(
            self.database_url(),
            poolclass=NullPool
        )
        session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        return session, engine

  