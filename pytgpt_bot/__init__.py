import telebot
import pytgpt.auto as text_generator
import pytgpt.imager as image_generator
from pytgpt.utils import Audio as audio_generator
from pytgpt.utils import Conversation
from functools import wraps
import logging

from .config import bot_token, max_tokens, timeout, voice, loglevel, logfile, admin_id
from .db import User, Chat

log_params = dict(
    format="%(asctime)s : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=loglevel,
)

if logfile:
    log_params["filename"] = logfile

logging.basicConfig(**log_params)

bot = telebot.TeleBot(bot_token, parse_mode="Markdown")

bot.remove_webhook()

logging.info(f"Bot started sucessfully. Admin ID - [{admin_id}]")


def handler_formatter(func):

    @wraps(func)
    def decorator(message: telebot.types.Message):
        try:
            logging.info(
                f"Serving user [{message.from_user.id}] ({message.from_user.full_name}) - Function [{func.__name__}]"
            )
            if message.text and message.text.startswith("/"):
                message.text = " ".join(message.text.split(" ")[1:])
            return func(message)
        except Exception as e:
            logging.error(f"Error on function - {func.__name__} - {e}")
            return bot.reply_to(
                message, text="An error occured and could't complete that request."
            )

    return decorator


@bot.message_handler(commands=["help", "start"])
@handler_formatter
def home(message: telebot.types.Message):
    """
    Welcome to [pytgpt](https://github.com/Simatwa/python-tgpt).
    /help : Show this help info.
    /chat : Chat with AI.
    /imager : Generate image from text. (default)
    /prodia : Generate image from text. (Prodia)
    /audio : Generate audio from text.
    /intro : Check current chat intro.
    /history : Check chat history.
    /sintro : Set new value for chat intro
    /reset : Start new chat thread.
    /myid : Echo your Telegram ID.
    /default : Chat with AI.
    """

    return bot.send_message(
        message.chat.id,
        text=home.__doc__,
    )


@bot.message_handler(commands=["myid"])
@handler_formatter
def echo_user_id(message: telebot.types.Message):
    return bot.reply_to(
        message,
        f"Greetings {message.from_user.first_name}. Your Telegram ID is {message.from_user.id}.",
    )


@bot.message_handler(commands=["sintro"])
@handler_formatter
def set_chat_intro(message: telebot.types.Message):
    """Set new value for chat intro"""
    if not len(message.text) > 10:
        return bot.reply_to(
            message, "The chat introduction must be at least 10 characters long."
        )
    user = User(message.from_user.id)
    user.update_intro(message.text)
    bot.reply_to(message, "New intro set successfully.")


@bot.message_handler(commands=["intro"])
@handler_formatter
def check_chat_intro(message: telebot.types.Message):
    user = User(message.from_user.id)
    return bot.reply_to(message, user.chat_intro)


@bot.message_handler(commands=["history"])
@handler_formatter
def check_chat_history(message: telebot.types.Message):
    user = User(message.from_user.id)
    return bot.reply_to(message, user.chat_history or "Your chat history is empty.")


@bot.message_handler(commands=["imager", "img"])
@handler_formatter
def text_to_image_default(message: telebot.types.Message):
    """Generate image using `imager`"""
    if not message.text:
        bot.reply_to(message, f"Text is required.")
    generator_obj = image_generator.Imager(
        timeout=30,
    )
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(
            message.text,
        )[0],
        caption=message.text,
    )


@bot.message_handler(commands=["prodia", "prod"])
@handler_formatter
def text_to_image_prodia(message: telebot.types.Message):
    """Generate image using `prodia`"""
    if not message.text:
        bot.reply_to(message, f"Text is required.")
    generator_obj = image_generator.Prodia(timeout=timeout)
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(message.text)[0],
        caption=message.text,
    )


@bot.message_handler(commands=["audio", "aud"])
@handler_formatter
def text_to_audio(message: telebot.types.Message):
    """Convert text to audio"""
    if not message.text:
        bot.reply_to(message, f"Text is required.")
    audio_chunk = audio_generator.text_to_audio(
        message=message.text,
        voice=voice,
        timeout=timeout,
    )
    return bot.send_audio(message.chat.id, audio=audio_chunk, caption=message.text)


@bot.message_handler(commands=["reset"])
@handler_formatter
def reset_chat(message: telebot.types.Message):
    """Reset current chat thread"""
    user = User(message.from_user.id)
    user.delete()
    return bot.reply_to(
        message,
        "New chat instance created.",
    )


@bot.message_handler(commands=["clear_database"])
@handler_formatter
def clear_chats(message: telebot.types.Message):
    """Delete all chat entries"""
    user = User(message.from_user.id)
    if not user.is_admin:
        return bot.reply_to(message, "Action resticted to admin only!")
    else:
        Chat.query("DELETE FROM Chat")
        logging.warning(
            f"Clearing Chats - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
        )
        return bot.reply_to(message, "Chats cleared successfully.")


@bot.message_handler(content_types=["text"])
@handler_formatter
def text_chat(message: telebot.types.Message):
    """Text generation"""
    user = User(message.from_user.id)
    chat_record = user.record
    conversation = Conversation(max_tokens=max_tokens)
    conversation.chat_history = chat_record.get("history") or ""
    conversation_prompt = conversation.gen_complete_prompt(
        message.text, intro=chat_record.get("intro")
    )
    bot.send_chat_action(message.chat.id, "typing")
    ai_response = text_generator.AUTO(is_conversation=False, timeout=timeout).chat(
        conversation_prompt
    )
    conversation.update_chat_history(
        prompt=message.text, response=ai_response, force=True
    )
    user.update_history(conversation.chat_history)
    return bot.send_message(message.chat.id, text=ai_response)


@bot.message_handler(func=lambda val: True)
def any_other_action(message):
    return bot.reply_to(message, home.__doc__)
