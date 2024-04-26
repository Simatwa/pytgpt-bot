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

### Commands


### Usage Information

This section provides detailed instructions on how to use the various commands available in the bot.

- **/start**: Displays the help information, offering a comprehensive list of available commands and their functionalities. This command is essential for users to quickly understand how to interact with the bot.

- **/chat**: Initiate a natural language conversation with the AI. This command allows users to engage in interactive dialogues, ask questions, or make requests.

- **/image**: Generates images from textual descriptions using the default provider. This feature enables users to visualize ideas or concepts through images.

- **/prodia**: Generates images from textual descriptions using the Prodia provider. This command offers a unique style or interpretation of the text descriptions compared to the default method.

- **/audio**: Converts text to speech, providing users with the ability to listen to descriptions, instructions, or any text content read out by the AI.

- **/intro**: Sets a new text for the chat intro. This command allows users to customize the chat introductory prompt which serves as a guide in the human-AI engagement.

- **/voice**: Sets a new voice for speech synthesis. This command enables users to choose from different voices for the AI to use when generating audio from text.

- **/provider**: Sets a new chat provider. This command allows users to switch between different providers for various functionalities, such as `phind`, `llama2`, `koboldai` etc.

- **/awesome**: Sets predefined prompt as `chat intro`. Browse over 200 of them.

- **/history**: Provides users with the ability to view the history of their chats with the bot. This command is useful for reviewing past interactions or finding specific information from previous conversations.

- **/check**: Offers an overview of the bot's current configuration, including any custom settings applied by the user.

- **/reset**: Resets the chat history and starts a new conversation thread. This command is useful for users who wish to start fresh or clear their chat history for privacy reasons.

- **/myid**: Echoes the user's Telegram ID. This command is useful for users who need to know their Telegram ID for various purposes, such as setting up bot admin.

- `any other text`: An alias for `/chat`, allowing users to continue with chatting.


### Administrative Commands


### Administrative Commands

- `/clear`: Clears all chats. This command is used to remove all chat data from the bot's database. It's a powerful command that should be used with caution, as it will delete all chat history.

- `/total`: Shows the total number of chats available. This command provides an overview of the current chat data stored in the bot's database, helping administrators understand the volume of interactions the bot has had.

- `/drop`: Clears the entire chat table and bot logs. Similar to `/clear`, this command removes all data from the chat table in the database. It's a more drastic measure than `/clear`, as it completely wipes out all chat data and current contents of log file.

- `/sql`: Allows running SQL statements against the database. This command provides a way for administrators to directly interact with the bot's database using SQL queries. It's a powerful tool for managing and analyzing the bot's data but should be used with caution to avoid unintended data loss or corruption.

- `/logs`: Checks the logs. This command is used to access the bot's logs, which can provide insights into the bot's activity, errors, and user interactions. It's a valuable tool for monitoring and troubleshooting the bot's performance.

## Support and Feedback

If you have any questions, feedback, or suggestions for `pytgpt`, please feel free to reach out. Your input is valuable in helping us improve and expand the bot's capabilities.

## License

`pytgpt-bot` is open-source and available under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as you see fit.

---

Thank you for using `pytgpt-bot`. Enjoy your AI-powered interactions!