from pathlib import Path

from setuptools import setup

ROOT_PATH = Path(__file__).parents[0]


def read_contents(path: str) -> str:
    full_path: Path = ROOT_PATH / path
    return full_path.read_text(encoding="utf-8")


setup(
    name="pytgpt-bot",
    packages=["pytgpt_bot"],
    version="0.1.1",
    license="MIT",
    author="Smartwa",
    maintainer="Smartwa",
    author_email="simatwacaleb@proton.me",
    description="Telegram bot for chatting, text-to-image and text-to-voice conversions",
    url="https://github.com/Simatwa/pytgpt-bot",
    project_urls={
        "Bug Report": "https://github.com/Simatwa/pytgpt-bot/issues/new",
        "Homepage": "https://github.com/Simatwa/pytgpt-bot",
        "Source Code": "https://github.com/Simatwa/pytgpt-bot",
        "Issue Tracker": "https://github.com/Simatwa/pytgpt-bot/issues",
        "Download": "https://github.com/Simatwa/pytgpt-bot/releases",
        "Documentation": "https://github.com/Simatwa/pytgpt-bot/blob/main/README.md",
    },
    entry_points={
        "console_scripts": [
            "pytgpt-bot = pytgpt_bot.cli:entry",
        ],
    },
    install_requires=[
        "pytelegrambotapi==4.17.0",
        "python-tgpt==0.6.6",
        "python-dotenv==1.0.0",
        "click==8.1.3",
        "SQLAlchemy==2.0.29",
    ],
    python_requires=">=3.10",
    keywords=[
        "ai",
        "tgpt",
        "pytgpt",
        "chatbot",
        "telegrambot",
        "pytelegrambot",
        "chatbot",
        "text-to-audio",
        "text-to-image",
    ],
    long_description=read_contents("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: Free For Home Use",
        "Intended Audience :: Customer Service",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
