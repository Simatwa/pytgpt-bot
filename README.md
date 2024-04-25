<p align="center">
<a href="https://github.com/Simatwa/pytgpt-bot/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=MIT&color=Blue&message=MIT&label=License"/></a>
<a href="#"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/pytgpt"/></a>
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

Proceed to fill the [env](env) configuration file as per the needs and then rename it `.env` before firing up the server `python3 run.py`.

Alternatively, using CLI interface::

   `$ pytgpt-bot run <Your Telegram Token>`

## Features

### Commands

- `/help`: This command displays the help information, providing users with a list of available commands and a brief description of what each command does. It's a useful way for users to quickly understand how to interact with the bot.

- `/chat`: Allows users to engage in natural language conversations with the AI. This command initiates a chat session where users can ask questions, make requests, or simply chat with the AI.

- `/image`: This command is used to generate images from text descriptions. Users can input a text description, and the bot will attempt to create an image based on that description. This feature can be particularly useful for visualizing ideas or concepts.

- `/prodia`: Similar to `/image`, this command also generates images from text descriptions. However, it uses a different provider (Prodia) to create the images. This could offer a different style or interpretation of the text descriptions compared to the default method.

- `/audio`: Converts text to speech. Users can input text, and the bot will generate an audio file that reads out the text. This can be useful for listening to descriptions, instructions, or any text content.

- `/sintro`: Allows users to set a new text for the chat intro. This can be used to customize the greeting message that users see when they start a new chat session with the bot.

- `/svoice`: Lets users set a new voice for speech synthesis. This command enables users to choose from different voices for the AI to use when generating audio from text.

- `/awesome`: Sets an awesome prompt as the introductory message for the chat. This could be a motivational quote, a fun fact, or any other type of prompt that might inspire or engage users in their interactions with the bot.

- `/history`: Checks the chat history. This command allows users to view the history of their chats with the bot. It can be useful for users who want to review past interactions or find specific information from previous conversations.

- `/settings`: Checks the current settings of the bot. This command provides users with an overview of the bot's current configuration, including any custom settings they have applied.

- `/reset`: Starts a new chat thread. This command resets the chat history and starts a new conversation thread. It's useful for users who want to start fresh or who want to clear their chat history for privacy reasons.

- `/myid`: Echoes the user's Telegram ID. This command is useful for users who need to know their Telegram ID for any reason, such as setting up bot admin.

- `/default`: Chat with AI. This command is essentially an alias for `/chat`, allowing users to initiate a chat session with the AI using a different command.

### Administrative Commands

- `/clear`: Clears all chats. This command is used to remove all chat data from the bot's database. It's a powerful command that should be used with caution, as it will delete all chat history.

- `/total`: Shows the total number of chats available. This command provides an overview of the current chat data stored in the bot's database, helping administrators understand the volume of interactions the bot has had.

- `/drop`: Clears the entire chat table. Similar to `/clear`, this command removes all data from the chat table in the database. It's a more drastic measure than `/clear`, as it completely wipes out all chat data.

- `/sql`: Allows running SQL statements against the database. This command provides a way for administrators to directly interact with the bot's database using SQL queries. It's a powerful tool for managing and analyzing the bot's data but should be used with caution to avoid unintended data loss or corruption.

## Support and Feedback

If you have any questions, feedback, or suggestions for `pytgpt`, please feel free to reach out. Your input is valuable in helping us improve and expand the bot's capabilities.

## License

`pytgpt-bot` is open-source and available under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as you see fit.

---

Thank you for using `pytgpt-bot`. Enjoy your AI-powered interactions!