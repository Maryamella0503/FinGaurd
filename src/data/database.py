import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./finguard.db",
)

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    step = Column(
        Integer,
        nullable=False,
    )

    transaction_type = Column(
        String,
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    oldbalance_org = Column(
        Float,
        nullable=False,
    )

    oldbalance_dest = Column(
        Float,
        nullable=False,
    )

    fraud_probability = Column(
        Float,
        nullable=False,
    )

    risk_level = Column(
        String,
        nullable=False,
    )

    decision = Column(
        String,
        nullable=False,
    )

    threshold = Column(
        Float,
        nullable=False,
    )

    model_version = Column(
        String,
        nullable=False,
    )


def create_tables():
    Base.metadata.create_all(
        bind=engine
    )