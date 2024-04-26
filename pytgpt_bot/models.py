from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, String
from pytgpt.utils import Conversation
from .config import database as database_str
from .config import provider as default_provider
from .config import voice

if not database_str:
    from .utils import path_to_default_db

    database_str: str = f"sqlite:///{path_to_default_db.as_posix()}"

engine = create_engine(database_str)

autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")

Session = sessionmaker(bind=autocommit_engine)

session = Session()

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    intro = Column(Text, default=Conversation.intro, nullable=False)
    provider = Column(String(20), default=default_provider, nullable=False)
    history = Column(Text, default="")
    voice = Column(String(30), default=voice, nullable=False)


def create_all():
    """Create tables from models"""
    Base.metadata.create_all(engine)


def drop_all():
    """Drop all tables created"""
    Base.metadata.drop_all(engine)


create_all()
