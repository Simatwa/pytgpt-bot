<p align="center">
<a href="https://github.com/Simatwa/pytgpt-bot/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=MIT&color=Blue&message=MIT&label=License"/></a>
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/static/v1?logo=Black&label=Code-style&message=Black"/></a>
<a href="https://pepy.tech/project/pytgpt-bot"><img src="https://static.pepy.tech/personalized-badge/pytgpt-bot?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads" alt="Downloads"></a>
<a href="https://github.com/Simatwa/pytgpt-bot/releases/latest"><img src="https://img.shields.io/github/downloads/Simatwa/pytgpt-bot/total?label=Asset%20Downloads&color=success" alt="Downloads"></img></a>
<a href="https://github.com/Simatwa/pytgpt-bot/releases"><img src="https://img.shields.io/github/v/release/Simatwa/pytgpt-bot?color=success&label=Release&logo=github" alt="Latest release"></img></a>
<a href="https://github.com/Simatwa/pytgpt-bot/releases"><img src="https://img.shields.io/github/release-date/Simatwa/pytgpt-bot?label=Release date&logo=github" alt="release date"></img></a>
<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com/Simatwa/pytgpt-bot"/></a>
<a href="https://wakatime.com/badge/github/Simatwa/pytgpt-bot"><img src="https://wakatime.com/badge/github/Simatwa/pytgpt-bot.svg" alt="wakatime"></a>
</p>

<h1 align="center">
Welcome to <a href="https://github.com/Simatwa/pytgpt-bot">pytgpt-bot</a>
</h1>

This is a Telegram bot based on [python-tgpt](https://github.com/Simatwa/python-tgpt), a powerful tool designed to enhance your interactions with AI. This bot is built on the robust foundation of the `pyTelegramBotAPI` and offers a wide range of features to make your experience with AI more engaging and interactive. Whether you're looking to chat with AI, generate images and audio from text, `pytgpt-bot` has got you covered.

## Installation

Clone repo and install dependencies.

```bash
git clone https://github.com/Simatwa/pytgpt-bot
cd pytgpt-bot
pip install -r requirements.txt
```

## Usage

Before getting started, ensure you've your Telegram bot token. If that's not the case then purpose to secure one from [@BotFather](https://telegram.me/BotFather).

Proceed to fill the [env](env) configuration file as per the needs and then rename it `.env` before firing up the server `python3 run.py`.

## Features

### 1. Chat with AI

- **Command**: `/chat`
- **Description**: Engage in a conversation with AI. This feature allows you to interact with the bot in a natural, conversational manner.

### 2. Generate Images from Text

- **Command**: `/imager`
- **Description**: Generate images from text descriptions. This feature uses AI to create visual representations of your text inputs, making it a fun and creative way to explore the capabilities of AI.

- **Variant**: `/prodia`
- **Description**: Generate images from text descriptions using the Prodia AI model. This variant offers a different style of image generation, providing a unique twist to your creative endeavors.

### 3. Generate Audio from Text

- **Command**: `/audio`
- **Description**: Generate audio from text. This feature allows you to convert your text inputs into spoken words, enabling you to listen to the AI's voice or use the audio for other purposes.

### 4. Check Current Chat Introduction

- **Command**: `/intro`
- **Description**: Check the current chat introduction. This feature allows you to view the introduction text set for the current chat, providing context and setting the tone for your interactions.

### 5. Check Chat History

- **Command**: `/history`
- **Description**: Check the chat history. This feature allows you to review past interactions within the chat, helping you to recall previous discussions and decisions.

### 6. Set New Value for Chat Introduction

- **Command**: `/sintro`
- **Description**: Set a new value for the chat introduction. This feature enables you to customize the introduction text for the current chat, allowing you to tailor the conversation to your preferences.

### 7. Start New Chat Thread

- **Command**: `/reset`
- **Description**: Start a new chat thread. This feature allows you to begin a fresh conversation with the bot, resetting the chat history and allowing for a new start.

### 8. Echo Your Telegram ID

- **Command**: `/myid`
- **Description**: Echo your Telegram ID. This feature provides you with your unique Telegram ID, useful for personalized interactions or for troubleshooting purposes and configuring admin.

### 9. Default Chat with AI

- **Command**: `/default`
- **Description**: Engage in a default chat with AI. This command is a shortcut to the `/chat` command, offering a quick and straightforward way to start a conversation with the bot.

## Getting Started

To get started with `pytgpt`, simply add the bot to your Telegram account and begin exploring the features. Each command is designed to be intuitive and user-friendly, making it easy to navigate and use the bot.

## Support and Feedback

If you have any questions, feedback, or suggestions for `pytgpt`, please feel free to reach out. Your input is valuable in helping us improve and expand the bot's capabilities.

## License

`pytgpt` is open-source and available under the MIT License. Feel free to use, modify, and distribute the code as you see fit.

---

Thank you for using `pytgpt`. Enjoy your AI-powered interactions!