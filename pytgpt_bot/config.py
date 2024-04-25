from dotenv import load_dotenv
from os import environ
from os import makedirs
from pytgpt.utils import api_static_dir

load_dotenv()

assert environ.get("token"), "Export bot's token to the environment 😠"

bot_token: str = environ.get("token")
admin_id: int = int(environ.get("admin-id", 1234567))
max_tokens: int = int(environ.get("max-tokens", 600))
timeout: int = int(environ.get("timeout", 30))
loglevel: int = int(environ.get("loglevel", 20))
logfile = environ.get("logfile")

bot_dir = api_static_dir / "bots"
path_to_db = bot_dir / "telegram.db"

makedirs(bot_dir, exist_ok=True)
