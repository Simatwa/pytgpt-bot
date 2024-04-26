import telebot
import json
import logging
import pytgpt.imager as image_generator
from pytgpt.utils import Audio as audio_generator
from pytgpt.utils import Conversation
from pytgpt.utils import AwesomePrompts
from functools import wraps
from sqlalchemy import text

from .config import (
    bot_token,
    max_tokens,
    timeout,
    loglevel,
    logfile,
    admin_id,
    provider,
)
from .db import User
from .utils import provider_keys
from .utils import provider_map
from .models import session, Chat, create_all, drop_all

chosen_provider: str = provider_map.get(provider)

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

bot = telebot.TeleBot(bot_token, disable_web_page_preview=True)

bot.remove_webhook()

logging.info(f"Bot started sucessfully. Admin ID - [{admin_id}]")

admin_commands = """
    /clear : Clear all chats.
    /total : Total chats available.
    /drop : Clear entire chat table and bot logs.
    /sql : Run sql statements against database.
    /logs : View bot logs.
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
                if admin and not User(message).is_admin:
                    return bot.reply_to(
                        message,
                        "Action restricted to admins only❗️",
                        reply_markup=make_delete_markup(message),
                    )

                if message.text and message.text.startswith("/"):
                    message.text = " ".join(message.text.split(" ")[1:])

                if text and not message.text:
                    return bot.reply_to(
                        message,
                        "Text is required❗️❗️.",
                        reply_markup=make_delete_markup(message),
                    )

                return func(message)
            except Exception as e:
                logging.error(f"Error on function - {func.__name__} - {e}")
                logging.debug(str(e))
                bot.reply_to(
                    message,
                    text="😔 An error occured and I could't complete that request ❗️❗️❗️",
                    reply_markup=make_delete_markup(message),
                )

        return decorator

    return main


def make_delete_markup(
    message: telebot.types.Message,
) -> telebot.types.InlineKeyboardMarkup:
    """Creates delete markup

    Args:
        message (telebot.types.Message):
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    callback_button = telebot.types.InlineKeyboardButton(
        text="🗑️", callback_data=f"delete:{message.chat.id}:{message.id}"
    )
    markup.add(callback_button)
    return markup


def send_and_add_delete_button(
    message: telebot.types.Message,
    text: str,
    as_reply: bool = False,
    parse_mode="Markdown",
):
    """Add send text and add delete inlineKeyboard item

    Args:
        message (telebot.types.Message):
        text (str): Tag
        as_reply (bool): Respond as a reply_to. Defaults to False.
        parse_mode (str): __. Defaults to Markdown.

    Returns:
        _type_: _description_
    """
    markup = make_delete_markup(message)
    return (
        bot.reply_to(message, text=text, reply_markup=markup, parse_mode=parse_mode)
        if as_reply
        else bot.send_message(
            message.chat.id, text, reply_markup=markup, parse_mode=parse_mode
        )
    )


def send_long_text(
    message: telebot.types.Message,
    text: str,
    add_delete: bool = False,
    parse_mode="Markdown",
):
    """Send texts longer than 4096 long

    Args:
        message (telebot.types.Message): Message object.
        text (str): Text to be sent.
        add_delete (bool). Add delete button. Defaults to False.
        parse_mode (str): __. Defaults to Markdown.
    """
    max_length = 4096
    take_action = send_and_add_delete_button if add_delete else bot.send_message
    if len(text) <= max_length:
        # bot.send_message(message.chat.id, text)
        take_action(
            message if add_delete else message.chat.id, text, parse_mode=parse_mode
        )
    else:
        parts = [text[i : i + max_length] for i in range(0, len(text), max_length)]
        for part in parts:
            take_action(
                message if add_delete else message.chat.id, part, parse_mode=parse_mode
            )


@bot.message_handler(commands=["help", "start"])
@handler_formatter()
def home(message: telebot.types.Message):
    """
    Welcome to [pytgpt-bot](https://github.com/Simatwa/pytgpt-bot).
    For chatting, text-to-image and text-to-voice conversions.
    /start : Show this help info.
    /chat : Chat with AI.
    /image : Generate image from text. (default)
    /prodia : Generate image from text. (Prodia)
    /audio : Generate audio from text.
    /intro : Set new text for chat intro.
    /voice : Set new voice for speech synthesis.
    /provider : Set new chat provider.
    /awesome : Set awesome prompt as intro.
    /history : Check chat history.
    /check : Check current settings.
    /reset : Start new chat thread.
    /myid : Echo your Telegram ID.
    /default : Chat with AI.
    """

    return bot.send_message(
        message.chat.id,
        text=(home.__doc__ + admin_commands if User(message).is_admin else ""),
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["myid"])
@handler_formatter()
def echo_user_id(message: telebot.types.Message):
    return bot.reply_to(
        message,
        f"Greetings {message.from_user.first_name}. Your Telegram ID is {message.from_user.id}.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["intro"])
@handler_formatter(text=True)
def set_chat_intro(message: telebot.types.Message):
    """Set new value for chat intro"""
    intro = AwesomePrompts().get_act(message.text) or message.text
    if not len(intro) > 10:
        return bot.reply_to(
            message,
            "The chat introduction must be at least 10 characters long.",
            reply_markup=make_delete_markup(message),
        )
    user = User(message)
    user.chat.intro = intro
    return bot.reply_to(
        message, "New intro set successfully.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["voice"])
@handler_formatter(text=False)
def set_new_speech_voice(message: telebot.types.Message):
    """Set new voice for speech synthesis"""
    user_id: str = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    make_item = lambda voice: telebot.types.InlineKeyboardButton(
        voice, callback_data=f"{voice}:{user_id}"
    )
    markup.add(*map(make_item, audio_generator.all_voices))
    bot.delete_message(message.chat.id, message.id)
    return bot.send_message(message.chat.id, "Choose a voice:", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in audio_generator.all_voices
)
def set_new_speech_voice_callback(call: telebot.types.CallbackQuery):
    """Set new voice for speech synthesis callback handler"""
    bot.delete_message(call.message.chat.id, call.message.id)
    voice, user_id = call.data.split(":")
    message = call.message
    markup = make_delete_markup(call.message)
    user = User(user_id=int(user_id))
    user.chat.voice = voice
    return bot.send_message(
        message.chat.id, f"New voice set : `{voice}`", reply_markup=markup
    )


@bot.message_handler(commands=["provider"])
@handler_formatter(text=False)
def set_new_text_provider(message: telebot.types.Message):
    """Set new text provider"""
    user_id: str = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    make_item = lambda provider: telebot.types.InlineKeyboardButton(
        provider, callback_data=f"{provider}:{user_id}"
    )
    markup.add(*map(make_item, provider_keys))
    bot.delete_message(message.chat.id, message.id)
    return bot.send_message(message.chat.id, "Choose a provider:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split(":")[0] in provider_keys)
def set_new_text_provider_callback(call: telebot.types.CallbackQuery):
    """Set new text provider callback handler"""
    bot.delete_message(call.message.chat.id, call.message.id)
    provider, user_id = call.data.split(":")
    message = call.message
    markup = make_delete_markup(call.message)
    user = User(user_id=int(user_id))
    user.chat.provider = provider
    return bot.send_message(
        message.chat.id, f"New text provider set : `{provider}`", reply_markup=markup
    )


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
    bot.delete_message(message.chat.id, message.id)
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
    user = User(user_id=int(user_id))
    user.chat.intro(awesome_prompts.get(awesome_prompt))
    return bot.send_message(
        call.message.chat.id,
        f"""New awesome-intro set:
```
{awesome_prompts.get(awesome_prompt)}
```.""",
        reply_markup=make_delete_markup(call.message),
    )


@bot.message_handler(commands=["check"])
@handler_formatter()
def check_current_settings(message: telebot.types.Message):
    """Check current user settings"""
    chat = User(message).chat
    current_user_settings = (
        f"Chat Length : `{len(chat.history)}`\n"
        f"Speech Voice : `{chat.voice}`\n"
        f"Chat Provider : `{chat.provider}`\n"
        f"Chat Intro : `{chat.intro}`"
    )
    return bot.reply_to(
        message,
        current_user_settings,
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["history"])
@handler_formatter()
def check_chat_history(message: telebot.types.Message):
    user = User(message)
    return send_long_text(
        message,
        user.chat.history or "Your chat history is empty ❗️",
        add_delete=True,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["image", "img"])
@handler_formatter(text=True)
def text_to_image_default(message: telebot.types.Message):
    """Generate image using `image`"""
    bot.send_chat_action(message.chat.id, "upload_photo", timeout=timeout)
    generator_obj = image_generator.Imager(
        timeout=timeout,
    )
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(
            message.text,
        )[0],
        caption=message.text,
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["prodia", "prod"])
@handler_formatter(text=True)
def text_to_image_prodia(message: telebot.types.Message):
    """Generate image using `prodia`"""
    bot.send_chat_action(message.chat.id, "upload_photo", timeout=timeout)
    generator_obj = image_generator.Prodia(timeout=timeout)
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(message.text)[0],
        caption=message.text,
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["audio", "aud"])
@handler_formatter(text=True)
def text_to_audio(message: telebot.types.Message):
    """Convert text to audio"""
    bot.send_chat_action(message.chat.id, "upload_audio", timeout=timeout)
    voice = User(message).chat.voice
    audio_chunk = audio_generator.text_to_audio(
        message=message.text,
        voice=voice,
        timeout=timeout,
    )
    return bot.send_audio(
        message.chat.id,
        audio=audio_chunk,
        caption=message.text,
        reply_markup=make_delete_markup(message),
        performer=voice,
        title="Text-to-Audio",
    )


@bot.message_handler(commands=["reset"])
@handler_formatter()
def reset_chat(message: telebot.types.Message):
    """Reset current chat thread"""
    user = User(message)
    user.delete()
    return bot.reply_to(
        message, "New chat instance created.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["clear", "clear_chats"])
@handler_formatter(admin=True)
def clear_chats(message: telebot.types.Message):
    """Delete all chat entries"""
    session.query(Chat).delete()
    logging.warning(
        f"Clearing Chats - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    return bot.reply_to(
        message, "Chats cleared successfully.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["total", "total_chats"])
@handler_formatter(admin=True)
def total_chats_query(message: telebot.types.Message):
    """Query total chats"""
    total_chats = session.query(Chat).count()
    logging.warning(
        f"Total Chats query - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    return bot.reply_to(
        message,
        f"Total Chats {total_chats}",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["drop", "drop_chats"])
@handler_formatter(admin=True)
def total_chats_table_and_logs(message: telebot.types.Message):
    """Drop chat table and create new"""
    if logfile:
        with open(logfile, "w") as fh:
            fh.write(
                f"ADMIN CLEARED LOGS & DROPPED CHAT TABLE [{message.from_user.id}] - ({message.from_user.full_name})\n"
            )
    logging.warning(
        f"Dropping Chat table and reinitialize - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    drop_all()
    create_all()
    return bot.reply_to(
        message,
        f"Chat table and bot logs dropped and new one created.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["sql"])
@handler_formatter(admin=True, text=True)
def run_sql_statement(message: telebot.types.Message):
    """Run sql statements against database"""
    logging.warning(
        f"Running SQL statements - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    try:
        results = session.execute(text(message.text))
        response: dict[str, list] = {}
        if results:
            for count, row in enumerate(results):
                response[count] = str(row)
            jsonified_response = json.dumps(
                response,
                indent=3,
            )
            response = f"```json\n{jsonified_response}\n```"
        else:
            response = f"```\n{results}\n```"
        session.commit()

    except Exception as e:
        response = f"{e.args[1] if e.args and len(e.args)>1 else e}"

    finally:
        return send_long_text(
            message,
            response,
            add_delete=True,
        )


@bot.message_handler(commands=["logs"])
@handler_formatter(admin=True)
def check_current_settings(message: telebot.types.Message):
    """View bot logs"""
    if not logfile:
        return bot.reply_to(message, "Logfile not specified!")
    with open(logfile, encoding="utf-8") as fh:
        contents: str = fh.read()
    return send_long_text(message, contents, add_delete=True, parse_mode=None)


@bot.message_handler(content_types=["text"])
@handler_formatter(text=True)
def text_chat(message: telebot.types.Message):
    """Text generation"""
    user = User(message)
    conversation = Conversation(max_tokens=max_tokens)
    conversation.chat_history = user.chat.history
    user_provider = provider_map.get(user.chat.provider)
    conversation_prompt = conversation.gen_complete_prompt(
        message.text, intro=user.chat.intro
    )
    bot.send_chat_action(message.chat.id, "typing")
    ai_response = user_provider(is_conversation=False, timeout=timeout).chat(
        conversation_prompt
    )
    conversation.update_chat_history(
        prompt=message.text, response=ai_response, force=True
    )
    user.chat.history = conversation.chat_history
    send_long_text(message, ai_response)


@bot.message_handler(func=lambda val: True)
def any_other_action(message):
    return bot.reply_to(message, home.__doc__, reply_markup=make_delete_markup(message))


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete:"))
def delete_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Delete callback handler"""
    action, trigger_chat_id, trigger_message_id = call.data.split(":")
    try:
        bot.delete_message(trigger_chat_id, trigger_message_id)
    except:
        pass
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
    except:
        pass
