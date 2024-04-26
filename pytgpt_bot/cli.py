import click
from pytgpt.utils import Audio
from pytgpt_bot import __version__
from os import environ
import logging
from pytgpt_bot.utils import provider_keys
from pytgpt_bot.utils import bot_dir
from shutil import rmtree

context_settings: dict = dict(auto_envvar_prefix="PYTGPT-BOT")

# bot_token, max_tokens, timeout, voice, loglevel, logfile, admin_id


@click.group()
@click.version_option(
    __version__, "-v", "--version", package_name="pytgpt-bot", prog_name="pytgpt-bot"
)
@click.help_option("-h", "--help")
def bot():
    """Telegram bot for text generation, text-to-image and text-to-audio conversions."""
    pass


@click.command(context_settings=context_settings)
@click.argument("token", required=True)
@click.option(
    "-m",
    "--max-tokens",
    type=click.IntRange(100, 30000),
    help="Maximum tokens to sample",
    default=600,
)
@click.option(
    "-t",
    "--timeout",
    type=click.IntRange(1, 300),
    help="Http request timeout in seconds",
    default=30,
)
@click.option(
    "-v",
    "--voice",
    type=click.Choice(Audio.all_voices),
    metavar="|".join(Audio.all_voices[:10]),
    help="The voice to use for speech synthesis",
    default="Brian",
)
@click.option(
    "-l",
    "--loglevel",
    type=click.Choice(["10", "20", "30", "40", "50", "51"]),
    default="20",
    help="Logging level",
    metavar="10|20|30|40|50|51",
)
@click.option(
    "-f",
    "--logfile",
    type=click.Path(),
    help="Path to file for loggging",
)
@click.option(
    "-a", "--admin-id", type=click.INT, help="Admin's Telegram user ID", default=12345
)
@click.option(
    "-p",
    "--provider",
    type=click.Choice(provider_keys),
    help="Default tgpt-based llm provider",
    default="auto",
)
@click.option(
    "-d",
    "--database",
    help="Database engine URL e.g sqlite:////:memory:",
)
@click.help_option("-h", "--help")
def run(**kwargs):
    """Start the bot"""
    click.secho("[*] Firing up bot - [pytgpt-bot]", fg="cyan")

    modded_kwargs: dict = {}

    for key, value in kwargs.items():
        modded_kwargs[key.replace("_", "-")] = str(value) if value else ""

    environ.update(modded_kwargs)
    try:
        from pytgpt_bot.main import bot

        bot.infinity_polling(timeout=kwargs.get("timeout"), skip_pending=True)
    except Exception as e:
        logging.error(e.args[1] if e.args and len(e.args) > 1 else str(e))
        click.secho("[^] Quitting", fg="yellow")


@click.command()
@click.option("-y", "--yes", is_flag=True, help="Okay to confirmations")
@click.help_option("-h", "--help")
def clear(yes: bool):
    """Clear bot's storage directory"""
    if not yes and not click.confirm(
        f"Are you sure to clear path '{bot_dir.as_posix()}'."
    ):
        return
    rmtree(bot_dir, ignore_errors=True)
    click.secho("[*] Path cleared successfully!", fg="yellow")


def entry():
    """Cli entrypoint"""
    bot.add_command(run)
    bot.add_command(clear)
    bot()


if __name__ == "__main__":
    entry()
