from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime
from pytgpt.utils import Conversation
from pytgpt_bot.config import database as database_str
from pytgpt_bot.config import provider as default_provider
from pytgpt_bot.config import voice
from datetime import datetime

if not database_str:
    from pytgpt_bot.utils import path_to_default_db

    database_str: str = f"sqlite:///{path_to_default_db.as_posix()}"

engine = create_engine(database_str)

autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

Session = sessionmaker(bind=autocommit_engine)

session = Session()

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"
    id = Column(String(20), primary_key=True)
    intro = Column(Text, default=Conversation.intro, nullable=False)
    provider = Column(String(20), default=default_provider, nullable=False)
    history = Column(Text, default="")
    voice = Column(String(30), default=voice, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Temp(Base):
    __tablename__ = "temps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(48), unique=True)
    prompt = Column(Text)
    provider = Column(String(20))
    updated_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def create_all():
    """Create tables from models"""
    Base.metadata.create_all(engine)


def drop_all():
    """Drop all tables created"""
    Base.metadata.drop_all(engine)


# drop_all()
create_all()
