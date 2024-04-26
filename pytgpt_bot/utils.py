from os import makedirs
from pytgpt.utils import api_static_dir

from pytgpt.opengpt import OPENGPT
from pytgpt.koboldai import KOBOLDAI
from pytgpt.phind import PHIND
from pytgpt.llama2 import LLAMA2
from pytgpt.blackboxai import BLACKBOXAI
from pytgpt.perplexity import PERPLEXITY
from pytgpt.yepchat import YEPCHAT
from pytgpt.auto import AUTO
from random import choice

provider_map: dict[str, object] = {
    "opengpt": OPENGPT,
    "koboldai": KOBOLDAI,
    "phind": PHIND,
    "llama2": LLAMA2,
    "blackboxai": BLACKBOXAI,
    "perplexity": PERPLEXITY,
    "yepchat": YEPCHAT,
    "auto": AUTO,
}

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
