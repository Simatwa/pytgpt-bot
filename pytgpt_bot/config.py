from dotenv import load_dotenv
from os import environ
from pytgpt.utils import Audio
from pytgpt_bot.utils import provider_keys

load_dotenv()

assert environ.get("token"), "Export bot's token to the environment 😠"

bot_token: str = environ.get("token")
database: str = environ.get("database")
provider: str = environ.get("provider", "auto")
admin_id: str = environ.get("admin-id", "")
max_tokens: int = int(environ.get("max-tokens", 600))
timeout: int = int(environ.get("timeout", 30))
loglevel: int = int(environ.get("loglevel", 20))
logfile = environ.get("logfile", "")
voice: str = environ.get("voice", "Brian")

assert (
    provider in provider_keys
), f"Provider '{provider}' is not one of {', '.join(provider_keys)}"


assert (
    voice in Audio.all_voices
), f"Voice '{voice}' is not one of {', '.join(Audio.all_voices)}"

admin_ids: list = admin_id.replace(" ", "").split(",")
