from os import makedirs, environ
from pytgpt.utils import api_static_dir
from pytgpt.async_providers import tgpt_mapper as provider_map
from pytgpt.auto import AsyncAUTO
from random import choice
import telebot
import pytgpt.gpt4free.utils as g4f_util

provider_map.update(
    dict(auto=AsyncAUTO),
)


emojis: dict[str, list[str]] = {
    "angry": [
        "😠",  # Angry Face
        "😡",  # Pouting Face
        "😤",  # Face with Steam From Nose
        "😖",  # Confounded Face
        "😞",  # Disappointed Face
        "😢",  # Loudly Crying Face
        "😣",  # Persevering Face
        "😥",  # Sweating Face
        "😰",  # Face with Open Mouth and Cold Sweat
        "😩",  # Weary Face
    ],
    "happy": [
        "😃",  # Grinning Face
        "😄",  # Grinning Face with Smiling Eyes
        "😁",  # Beaming Face with Smiling Eyes
        "😆",  # Grinning Squinting Face
        "😅",  # Grinning Face with Sweat
        "😂",  # Face with Tears of Joy
        "🤣",  # Rolling on the Floor Laughing
        "😊",  # Smiling Face with Smiling Eyes
        "😇",  # Smiling Face with Halo
        "😍",  # Smiling Face with Heart-Eyes
    ],
    "love": [
        "😍",  # Smiling Face with Heart-Eyes
        "😘",  # Face Blowing a Kiss
        "😚",  # Kissing Face with Closed Eyes
        "😙",  # Kissing Face with Smiling Eyes
        "😗",  # Face with Tongue and Winking Eye
        "😚",  # Kissing Face with Closed Eyes
        "😜",  # Grinning Face with Sweat
        "😝",  # Grinning Face with Sweat
        "😛",  # Grinning Face with Big Eyes
        "😳",  # Flushed Face
    ],
}

provider_keys: list = list(provider_map.keys())
emoji_keys: list[str] = list(emojis.keys())

bot_dir = api_static_dir / "bots"
path_to_default_db = bot_dir / "telegram.db"


makedirs(bot_dir, exist_ok=True)


def get_random_emoji(mood: str = None) -> str:
    """Generate random emoji best on mood

    Args:
        mood (str): angry|sad Defaults to Random.

    Returns:
        str: emoji
    """
    if not mood:
        mood = choice(emoji_keys)
    return choice(emojis[mood])


def make_delete_markup(
    message: telebot.types.Message,
) -> telebot.types.InlineKeyboardMarkup:
    """Creates delete markup

    Args:
        message (telebot.types.Message):
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    callback_button = telebot.types.InlineKeyboardButton(
        text="🗑️", callback_data=f"delete:{message.chat.id}:{message.id}"
    )
    markup.add(callback_button)
    return markup


def get_user_id(
    message: telebot.types.Message | telebot.types.CallbackQuery = None,
    user_id: int | str = None,
) -> str:
    """Extract id from Message obj or user_id

    Args:
        message (telebot.types.Message): Message object. Defaults to None.
        user_id (int|str): User id. Defaults to None.

    Returns:
        int: PositiveInt
    """
    assert message or user_id, "Message or User id is required."

    if user_id is not None:
        user_id = str(user_id)

    elif message.chat.type == "private":
        user_id = str(message.from_user.id)

    else:
        user_id = str(message.chat.id)

    return user_id[1:] if user_id[0] == "-" else user_id


def get_g4f_providers() -> list[str]:
    """Working gpt4free providers

    Returns:
        list[str]: Provider names.
    """
    g4f_test = g4f_util.TestProviders(
        quiet=True,
        do_log=True,
    ).get_results(run=str(environ.get("test-g4f", "false")).lower() == "true")
    working = []
    for result in g4f_test:
        working.append(result["name"])
    return working
