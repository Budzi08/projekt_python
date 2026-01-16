"""
Moduł konfiguracji bazy danych.

Zawiera konfigurację połączenia z bazą SQLite oraz fabrykę sesji.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator

SQLALCHEMY_DATABASE_URL: str = "sqlite:///./blackjack.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """
    Generator sesji bazy danych.
    
    Tworzy sesję bazy danych i zapewnia jej prawidłowe zamknięcie
    po zakończeniu operacji.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
