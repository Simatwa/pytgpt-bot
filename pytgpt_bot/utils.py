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

provider_keys: list = list(provider_map.keys())

bot_dir = api_static_dir / "bots"
path_to_default_db = bot_dir / "telegram.db"

makedirs(bot_dir, exist_ok=True)
