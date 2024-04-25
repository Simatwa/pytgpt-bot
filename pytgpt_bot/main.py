import telebot
import pytgpt.auto as text_generator
import pytgpt.imager as image_generator
from pytgpt.utils import Audio as audio_generator
from pytgpt.utils import Conversation
from pytgpt.utils import AwesomePrompts
from functools import wraps
import logging

from .config import bot_token, max_tokens, timeout, voice, loglevel, logfile, admin_id
from .db import User, Chat

log_params = dict(
    format="%(asctime)s : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=loglevel,
)

awesome_prompts: dict = AwesomePrompts().get_acts()
awesome_prompts_keys: list = list(awesome_prompts.keys())

if logfile:
    log_params["filename"] = logfile

logging.basicConfig(**log_params)

bot = telebot.TeleBot(bot_token, parse_mode="Markdown")

bot.remove_webhook()

logging.info(f"Bot started sucessfully. Admin ID - [{admin_id}]")

admin_commands = """
    /clear : Clear all chats.
    /total : Total chats available.
    /drop : Clear entire chat table.
    /sql : Run sql statements against database.
"""


def handler_formatter(text: bool = False, admin: bool = False):
    """Handles common message handler verification and execptions

    Args:
        text (bool, optional): Command must contain text?. Defaults to False.
        admin (bool, optional): Needs admin privileges?. Defaults to False.
    """

    def main(func):

        @wraps(func)
        def decorator(message: telebot.types.Message):
            try:
                logging.info(
                    f"Serving user [{message.from_user.id}] ({message.from_user.full_name}) - Function [{func.__name__}]"
                )
                if admin and not User(message.from_user.id).is_admin:
                    return bot.reply_to(message, "Action restricted to admins only!")

                if message.text and message.text.startswith("/"):
                    message.text = " ".join(message.text.split(" ")[1:])

                if text and not message.text:
                    return bot.reply_to(message, "Text is required.")

                return func(message)
            except Exception as e:
                logging.error(f"Error on function - {func.__name__} - {e}")
                logging.exception(e)
                return bot.reply_to(
                    message, text="An error occured and could't complete that request."
                )

        return decorator

    return main


def send_long_text(message: telebot.types.Message, text: str):
    """Send texts longer than 4096 long

    Args:
        message (telebot.types.Message): Message object.
        text (str): Text to be sent.
    """
    max_length = 4096
    if len(text) <= max_length:
        bot.send_message(message.chat.id, text)
    else:
        parts = [text[i : i + max_length] for i in range(0, len(text), max_length)]
        for part in parts:
            bot.send_message(message.chat.id, part)


@bot.message_handler(commands=["help", "start"])
@handler_formatter()
def home(message: telebot.types.Message):
    """
    Welcome to [pytgpt-bot](https://github.com/Simatwa/pytgpt-bot).
    /help : Show this help info.
    /chat : Chat with AI.
    /imager : Generate image from text. (default)
    /prodia : Generate image from text. (Prodia)
    /audio : Generate audio from text.
    /sintro : Set new text for chat intro.
    /svoice : Set new voice for speech synthesis.
    /awesome : Set awesome prompt as intro.
    /history : Check chat history.
    /settings : Check current settings.
    /reset : Start new chat thread.
    /myid : Echo your Telegram ID.
    /default : Chat with AI.
    """

    return bot.send_message(
        message.chat.id,
        text=(
            home.__doc__ + admin_commands if User(message.from_user.id).is_admin else ""
        ),
    )


@bot.message_handler(commands=["myid"])
@handler_formatter()
def echo_user_id(message: telebot.types.Message):
    return bot.reply_to(
        message,
        f"Greetings {message.from_user.first_name}. Your Telegram ID is {message.from_user.id}.",
    )


@bot.message_handler(commands=["sintro"])
@handler_formatter(text=True)
def set_chat_intro(message: telebot.types.Message):
    """Set new value for chat intro"""
    intro = AwesomePrompts().get_act(message.text) or message.text
    if not len(intro) > 10:
        return bot.reply_to(
            message, "The chat introduction must be at least 10 characters long."
        )
    user = User(message.from_user.id)
    user.update_intro(intro)
    bot.reply_to(message, "New intro set successfully.")


@bot.message_handler(commands=["svoice"])
@handler_formatter(text=False)
def set_new_chat_intro(message: telebot.types.Message):
    """Set new voice for speech synthesis"""
    user_id: str = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    make_item = lambda voice: telebot.types.InlineKeyboardButton(
        voice, callback_data=f"{voice}:{user_id}"
    )
    markup.add(*map(make_item, audio_generator.all_voices))

    return bot.send_message(message.chat.id, "Choose a voice:", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in audio_generator.all_voices
)
def set_new_chat_intro_callback(call: telebot.types.CallbackQuery):
    """Set new voice for speech synthesis callback handler"""
    bot.delete_message(call.message.chat.id, call.message.id)
    voice, user_id = call.data.split(":")
    message = call.message
    if not voice in audio_generator.all_voices:
        return bot.reply_to(
            message,
            f"Voice '{voice}' is not one of : `({', '.join(audio_generator.all_voices)})`",
        )
    user = User(int(user_id))
    user.update_voice(voice)
    return bot.send_message(message.chat.id, f"New voice set : `{voice}`")


@bot.message_handler(commands=["awesome"])
@handler_formatter(text=False)
def set_awesome_prompt_as_chat_intro(message: telebot.types.Message):
    """Set awesome prompt as intro"""
    user_id: str = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    make_item = lambda awesome: telebot.types.InlineKeyboardButton(
        awesome, callback_data=f"{awesome}:{user_id}"
    )
    markup.add(*map(make_item, awesome_prompts_keys))
    return bot.send_message(message.chat.id, "Choose awesome:", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in awesome_prompts_keys
)
def set_awesome_prompt_as_chat_intro_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Set awesome prompt as intro callback handler"""
    bot.delete_message(call.message.chat.id, call.message.id)
    awesome_prompt, user_id = call.data.split(":")
    user = User(int(user_id))
    user.update_intro(awesome_prompts.get(awesome_prompt))
    return bot.send_message(
        call.message.chat.id,
        f"""New awesome-intro set:
```
{awesome_prompts.get(awesome_prompt)}
```.""",
    )


@bot.message_handler(commands=["settings"])
@handler_formatter()
def check_current_settings(message: telebot.types.Message):
    """Check current user settings"""
    user = User(message.from_user.id)
    current_user_settings = f"""
    **Chat Length** : `{len(user.chat_history)}`
    **Speech Voice** : `{user.chat_voice}`
    **Chat Intro** : `{user.chat_intro}`
    """
    return bot.reply_to(message, current_user_settings)


@bot.message_handler(commands=["history"])
@handler_formatter()
def check_chat_history(message: telebot.types.Message):
    user = User(message.from_user.id)
    return send_long_text(message, user.chat_history or "Your chat history is empty.")


@bot.message_handler(commands=["image", "img"])
@handler_formatter(text=True)
def text_to_image_default(message: telebot.types.Message):
    """Generate image using `image`"""
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
@handler_formatter(text=True)
def text_to_image_prodia(message: telebot.types.Message):
    """Generate image using `prodia`"""
    generator_obj = image_generator.Prodia(timeout=timeout)
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(message.text)[0],
        caption=message.text,
    )


@bot.message_handler(commands=["audio", "aud"])
@handler_formatter(text=True)
def text_to_audio(message: telebot.types.Message):
    """Convert text to audio"""
    audio_chunk = audio_generator.text_to_audio(
        message=message.text,
        voice=User(message.chat.id).chat_voice,
        timeout=timeout,
    )
    return bot.send_audio(message.chat.id, audio=audio_chunk, caption=message.text)


@bot.message_handler(commands=["reset"])
@handler_formatter()
def reset_chat(message: telebot.types.Message):
    """Reset current chat thread"""
    user = User(message.from_user.id)
    user.delete()
    return bot.reply_to(
        message,
        "New chat instance created.",
    )


@bot.message_handler(commands=["clear", "clear_chats"])
@handler_formatter(admin=True)
def clear_chats(message: telebot.types.Message):
    """Delete all chat entries"""
    Chat.query("DELETE FROM Chat")
    logging.warning(
        f"Clearing Chats - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    return bot.reply_to(message, "Chats cleared successfully.")


@bot.message_handler(commands=["total", "total_chats"])
@handler_formatter(admin=True)
def total_chats_query(message: telebot.types.Message):
    """Query total chats"""
    total_chats = Chat.query("SELECT COUNT(id) FROM Chat")[0][0]
    logging.warning(
        f"Total Chats query - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    return bot.reply_to(message, f"Total Chats **{total_chats}**")


@bot.message_handler(commands=["drop", "drop_chats"])
@handler_formatter(admin=True)
def total_chats_table(message: telebot.types.Message):
    """Drop chat table and create new"""
    logging.warning(
        f"Dropping Chat table and reinitialize - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    Chat.query("DROP TABLE CHAT")
    Chat.initialize()
    return bot.reply_to(message, f"Chat table dropped and new one created.")


@bot.message_handler(commands=["sql"])
@handler_formatter(admin=True)
def run_sql_statement(message: telebot.types.Message):
    """Run sql statements against database"""
    logging.warning(
        f"Running SQL statements - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    try:
        response = f"""
        ```
        {Chat.query(message.text)}
        ```
        """

    except Exception as e:
        response = f"ERROR : {e.args[1] if e.args and len(e.args)>1 else e}"

    finally:
        return send_long_text(message, response)


@bot.message_handler(content_types=["text"])
@handler_formatter(text=True)
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
    return send_long_text(message, ai_response)


@bot.message_handler(func=lambda val: True)
def any_other_action(message):
    return bot.reply_to(message, home.__doc__)
