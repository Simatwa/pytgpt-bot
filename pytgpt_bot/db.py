import sqlite3
from .config import admin_id
from .config import path_to_db
from functools import wraps
import logging
import typing
from pytgpt.utils import Conversation


def exception_handler(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Error on function" f" '{func.__name__}' - " f"{e}")

    return decorator


class Chat:
    """Performs CRUD operations on dbs"""

    @staticmethod
    @exception_handler
    def initialize():
        """Creates database"""
        conn = sqlite3.connect(path_to_db)
        conn.execute(
            f"""
        CREATE TABLE IF NOT EXISTS Chat(
            Id INTEGER PRIMARY KEY,
            Intro TEXT DEFAULT "{Conversation.intro}",
            History TEXT);
        """
        )
        conn.commit()

    @staticmethod
    @exception_handler
    def insert(**kwargs):
        """Inserts data
        Kwargs:  {
           field : data
        }
        """
        fields: list[str] = list(kwargs.keys())
        values: tuple[str] = tuple(kwargs.values())
        conn = sqlite3.connect(path_to_db)
        csr = conn.cursor()
        sql = (
            "INSERT INTO Chat"
            f"({', '.join(fields)}) "
            f"VALUES ({ '?,'*(len(values)-1) + '?' if len(values) > 1 else '?'})"
        )
        csr.execute(sql, values)
        csr.close()
        conn.commit()
        conn.close()

    @staticmethod
    @exception_handler
    def update(id, field, data):
        """Update record
        Args:
           id : User id
           field : Column name.
           data : Data value.
        """
        conn = sqlite3.connect(path_to_db)
        csr = conn.cursor()
        csr.execute(f"UPDATE  Chat SET  {field} = ?  WHERE id = ?" "", (data, id))
        csr.close()
        conn.commit()
        conn.close()

    @staticmethod
    @exception_handler
    def read(id: int, fetchone: bool = False) -> list[tuple]:
        """Read user data

        Args:
            id (int): User id
            fetchone (bool): Return first entry only. Defaults to False.

        Returns:
            tuple[tuple]: User data
        """
        conn = sqlite3.connect(path_to_db)
        csr = conn.cursor()
        csr.execute("SELECT * FROM Chat WHERE Id = ?", (id,))
        all_entries = csr.fetchone() if fetchone else csr.fetchall()
        csr.close()
        conn.close()
        return all_entries

    @staticmethod
    @exception_handler
    def delete(id: int):
        """Delete chat

        Args:
            id (int): User id

        Returns:
            None: None
        """
        conn = sqlite3.connect(path_to_db)
        conn.execute(f"DELETE FROM Chat WHERE ID={id}")
        conn.commit()
        conn.close()

    @staticmethod
    @exception_handler
    def query(sql: str) -> typing.Union[tuple[tuple], typing.NoReturn]:
        """Run sql commands and return entries"""
        conn = sqlite3.connect(path_to_db)
        csr = conn.cursor()
        csr.execute(sql)
        entries = csr.fetchall()
        csr.close()
        conn.commit()
        conn.close()
        return entries


class User(Chat):
    """User chat model"""

    def __init__(self, id: int):
        """Constructor

        Args:
            id (int): User id
        """
        self.id = id
        if Chat.read(self.id, True) is None:
            Chat.insert(id=self.id)

    @property
    def is_admin(self) -> bool:
        """Checks user admin status"""
        return self.id == admin_id

    @property
    def record(self) -> typing.Dict[str, typing.Union[int, str]]:
        """User data

        Returns:
            typing.Dict[str, typing.Union[int, str]]: Records
        """
        id, intro, history = Chat.read(id=self.id, fetchone=True)
        return dict(id=id, intro=intro, history=history)

    @property
    def chat_history(self) -> typing.Union[str, None]:
        """User's chat history"""
        return self.record.get("history")

    @property
    def chat_intro(self) -> str:
        """User's chat intro"""
        return self.record.get("intro")

    def update_history(self, data: str):
        """Update chat history

        Args:
            data (str): New history
        """
        Chat.update(
            self.id,
            field="history",
            data=data,
        )

    def update_intro(self, data: str):
        """Update chat intro

        Args:
            data (str): New intro.
        """
        Chat.update(
            self.id,
            field="intro",
            data=data,
        )

    def delete(self):
        """Delete current user account"""
        Chat.delete(self.id)


# import os
# os.remove(path_to_db)
Chat.initialize()
# exit()
# resp = User(113)
# resp.update_intro('hello world')
# resp.chat_history('hello')
# resp.delete()
# resp = User(113)
# print(resp.chat_intro)
