from .models import Chat
from .models import session
from .config import admin_id
from telebot.types import Message


class User:
    """User dummy model"""

    def __init__(self, message: Message = None, user_id: int = None):
        """Constructor

        Args:
            message (telebot.types.Message): Message object. Defaults to None.
            user_id (int): User id. Defaults to None
        """
        assert message or user_id, "Message or User id is required."
        id = user_id or message.from_user.id
        chat = session.query(Chat).filter_by(id=id).first()
        if chat:
            # chat exist
            self.chat = chat
        else:
            self.chat = Chat(id=id)
            session.add(self.chat)
            session.commit()

    @property
    def is_admin(self) -> bool:
        """Checks user admin status"""
        return self.chat.id == admin_id

    def delete(self) -> None:
        """Delete user"""
        session.delete(self.chat)
