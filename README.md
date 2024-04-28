<p align="center">
<a href="https://github.com/Simatwa/pytgpt-bot/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=MIT&color=Blue&message=MIT&label=License"/></a>
<a href="#"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/pytgpt-bot"/></a>
<a href="https://pypi.org/project/pytgpt-bot"><img alt="PyPi" src="https://img.shields.io/pypi/v/pytgpt-bot?color=green"/></a>
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
<a href="https://pepy.tech/project/pytgpt-bot"><img src="https://static.pepy.tech/personalized-badge/pytgpt-bot?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads" alt="Downloads"></a>
<!--
<a href="https://github.com/Simatwa/pytgpt-bot/releases"><img src="https://img.shields.io/github/v/release/Simatwa/pytgpt-bot?color=success&label=Release&logo=github" alt="Latest release"></img></a> 
-->
<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com/Simatwa/pytgpt-bot"/></a>
<a href="https://wakatime.com/badge/github/Simatwa/pytgpt-bot"><img src="https://wakatime.com/badge/github/Simatwa/pytgpt-bot.svg" alt="wakatime"></a>
</p>

<h1 align="center">
Welcome to <a href="https://t.me/pytgpt_bot">pytgpt-bot</a>
</h1>

This is a Telegram bot based on [python-tgpt](https://github.com/Simatwa/python-tgpt), a powerful tool designed to enhance your interactions with AI. This bot is built on the robust foundation of the `pyTelegramBotAPI` and offers a wide range of features to make your experience with AI more engaging and interactive. Whether you're looking to chat with AI, generate images and audio from text, `pytgpt-bot` has got you covered.

## Prerequisites

- [x] [Python>=3.10](https://python.org)

## Installation

1. From Source

Clone repo and install.

```bash
git clone https://github.com/Simatwa/pytgpt-bot.git
cd pytgpt-bot
pip install .
```

2. From Pypi *(recommended)*

```sh
pip install pytgpt-bot
```

## Usage

Before getting started, ensure you've your Telegram bot token. If that's not the case then purpose to secure one from [@BotFather](https://telegram.me/BotFather).

Proceed to fill the [env](env) configuration file as per the needs and then rename it `.env` before firing up the bot `python3 run.py`.

Alternatively, using CLI:

   `$ pytgpt-bot run <Your Telegram Token>`

## Features

### Access Commands

- **/start**: This command shows you how to use the bot. It's like a guidebook for all the commands and what they do.

- **/chat**: Use this to talk to the AI. You can ask questions, make requests, or just chat about anything.

- **/image**: Want to see what something looks like? Type a description, and this command will create an image for you.

- **/prodia**: Similar to `/image`, but it gives you a different style of image.

- **/speak**: If you prefer listening to text instead of reading it, use this command to have the AI read out text for you.

- **/intro**: Sets a new text for the chat intro.

- **/voice**: Choose how the AI's voice sounds when it reads out text.

- **/provider**: Switch between different AI providers for various features.

- **/awesome**: Browse through a selection of cool chat intros.

- **/history**: See past conversations with the bot.

- **/check**: See what settings are currently active for your bot.

- **/reset**: Start a new conversation from scratch.

- **/myid**: Find out your Telegram ID.

- **/suspend**: Temporarily stop the bot from responding.

- **/resume**: Restart the bot after it's been suspended.

- **Any other text**: Just type anything to continue chatting.

### Administrative Commands

- **/clear**: Remove all chat data from the bot's database. Be careful with this one!

- **/total**: See how many chats the bot has had.

- **/drop**: Delete everything from the chat table and bot logs. This is more extreme than `/clear`.

- **/sql**: Run SQL queries on the bot's database. Use this with caution!

- **/logs**: Check the bot's logs for activity, errors, and user interactions.

- `any other text`: An alias for `/chat`, allowing users to continue with chatting.

> [!TIP]
> For a better understanding of these commands, try interacting with a running bot from [@pytgpt_bot](https://t.me/pytgpt_bot). This can give you a practical idea of how the bot works and how to use it effectively.

### Administrative Commands

- **/clear**: Use this command to remove all chat data from the bot's database. It's a powerful tool, so use it carefully to avoid losing important data.

- **/total**: This command shows you the total number of chats the bot has handled. It's a quick way to see how much interaction the bot has had.

- **/drop**: If you need to completely wipe out all chat data and logs, use this command. It's more extreme than `/clear` and should be used with caution to avoid losing all data.

- **/sql**: Want to directly interact with the bot's database? This command lets you run SQL queries. It's a powerful feature for managing and analyzing data, but be cautious to avoid mistakes.

- **/logs**: This command gives you access to the bot's logs. It's useful for monitoring the bot's activity, spotting errors, and understanding user interactions.

> [!IMPORTANT]
> Administrative commands are restricted to the users whose Telegram IDs are specified in the [.env](https://github.com/Simatwa/pytgpt-bot/blob/308f6079d153a429c445649896840fdc7cbfac11/env#L12) file.

## Further Tips

- The bot features inline query for text generation. The query must end with *three ellipsis* `...`. Remember to enable the mode from [@BotFather](https://t.me/pytgpt_bot). `/setinline`
- You can as well add the bot to a Telegram channel. Grant it read and delete permissions. The access commands will still work out. `@bot_username <text>` will trigger **text generation**.
- Channel Admin will control the bot access using the `/suspend` and `/resume` commands. *(Experimental).*

## Support and Feedback

If you have any questions, feedback, or suggestions for `pytgpt`, please feel free to reach out. Your input is valuable in helping us improve and expand the bot's capabilities.

## License

`pytgpt-bot` is open-source and available under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as you see fit.

---

Thank you for using `pytgpt-bot`. Enjoy your AI-powered interactions!