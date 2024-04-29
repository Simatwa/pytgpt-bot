#!/usr/bin/python3
from dotenv import load_dotenv
from pathlib import Path
import os

root_path = Path(__file__).parent
dotenv_path = root_path / ".env"
load_dotenv(dotenv_path)

from pytgpt_bot.main import bot

if __name__ == "__main__":
    timeout = int(os.environ.get("timeout", 30))
    bot.infinity_polling(
        timeout=timeout,
        skip_pending=str(os.environ.get("skip-pending", "true")).lower() == "true",
        long_polling_timeout=timeout,
    )
