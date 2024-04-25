from dotenv import load_dotenv
from pathlib import Path
import os

root_path = Path(__file__).parent
dotenv_path = root_path / ".env"
load_dotenv(dotenv_path)

from pytgpt_bot.main import bot

if __name__ == "__main__":
    bot.infinity_polling(timeout=int(os.environ.get("timeout", 30)))
