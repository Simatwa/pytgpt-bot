from telebot.custom_filters import SimpleCustomFilter
from telebot import types, TeleBot
from telebot.util import extract_command, extract_arguments
from pytgpt_bot.db import User
from pytgpt_bot.config import admin_ids


class IsActiveFilter(SimpleCustomFilter):
    """Checks if Bot is set on/off"""

    key: str = "is_chat_active"

    def check(self, message: types.Message | types.CallbackQuery):
        if isinstance(message, types.CallbackQuery):
            return User(message.message).chat.is_active
        return User(message).chat.is_active


class IsBotOwnerFilter(SimpleCustomFilter):
    """Checks whether the user is the BOT admin"""

    key: str = "is_bot_owner"

    def check(self, message: types.Message):
        return str(User(message).chat.id) in admin_ids


class IsAdminFilter(SimpleCustomFilter):
    """
    Check whether the user is administrator / owner of the chat.

    .. code-block:: python3
        :caption: Example on using this filter:

        @bot.message_handler(chat_types=['supergroup'], is_chat_admin=True)
        # your function
    """

    key = "is_chat_admin"

    def __init__(self, bot):
        self._bot = bot

    def check(self, message: types.Message | types.CallbackQuery):
        """
        :meta private:
        """
        if isinstance(message, types.CallbackQuery):
            return self._bot.get_chat_member(
                message.message.chat.id, message.from_user.id
            ).status in ["creator", "administrator"]

        elif message.chat.type == "private":
            return True

        return self._bot.get_chat_member(
            message.chat.id, message.from_user.id
        ).status in ["creator", "administrator"]


class IsBotTaggedFilter(SimpleCustomFilter):
    """Checks if bot is tagged"""

    key: str = "is_bot_tagged"

    def __init__(self, bot_info: types.User):
        """Constructor

        Args:
            bot_info (types.User): Bot info.
        """
        self.bot_info = bot_info

    def check(self, message: types.Message):
        if message.text:
            return "@" + self.bot_info.username == message.text.split(" ")[0]

        return False


class IsChatCommandFilter(SimpleCustomFilter):
    """Checks if text parsed is for tex-generation"""

    key: str = "is_chat_command"

    def check(self, message: types.Message):
        command = extract_command(message.text)
        return command == "chat" if command else True
