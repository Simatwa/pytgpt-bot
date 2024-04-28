from pytgpt_bot.models import Chat
from pytgpt_bot.models import session
from pytgpt_bot.config import admin_id
from telebot.types import Message, CallbackQuery


class User:
    """User dummy model"""

    def __init__(self, message: Message | CallbackQuery = None, user_id: int = None):
        """Constructor

        Args:
            message (telebot.types.Message): Message object. Defaults to None.
            user_id (int): User id. Defaults to None
        """
        assert message or user_id, "Message or User id is required."

        if user_id:
            id = user_id

        elif message.chat.type == "private":
            id = message.from_user.id

        else:
            id = message.chat.id

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
