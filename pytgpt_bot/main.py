import telebot
import json
import logging
import asyncio
from telebot.async_telebot import AsyncTeleBot
import telebot.util as telebot_util
import pytgpt.imager as image_generator
from pytgpt.utils import Audio as audio_generator
from pytgpt.utils import Conversation
from pytgpt.utils import AwesomePrompts
from pytgpt.gpt4free import AsyncGPT4FREE
from functools import wraps
from sqlalchemy import text
from uuid import uuid4

from pytgpt_bot import __version__, __repo__

from pytgpt_bot.config import (
    bot_token,
    max_tokens,
    timeout,
    loglevel,
    logfile,
    admin_ids,
)
from pytgpt_bot.db import User
from pytgpt_bot.utils import (
    provider_keys,
    get_random_emoji,
    provider_map,
    make_delete_markup,
    get_user_id,
    get_g4f_providers,
)
from pytgpt_bot.models import session, Chat, Temp, create_all, drop_all
from pytgpt_bot.filters import (
    IsActiveFilter,
    IsBotOwnerFilter,
    IsAdminFilter,
    IsBotTaggedFilter,
    IsChatCommandFilter,
)


log_params = dict(
    format="%(asctime)s : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=loglevel,
)

if logfile:
    log_params["filename"] = logfile

logging.basicConfig(**log_params)


bot = AsyncTeleBot(bot_token, disable_web_page_preview=True)

loop = asyncio.get_event_loop()

logging.info(
    f"Bot started sucessfully {get_random_emoji('happy')}. Admin IDs - [{', '.join(admin_ids)}]"
)

asyncio.run(bot.remove_webhook())

awesome_prompts_dict: dict = AwesomePrompts().get_acts()
awesome_prompts_keys: list = list(awesome_prompts_dict.keys())
g4f_providers = get_g4f_providers()

usage_info = (
    "Welcome to [PYTGPT-BOT](https://github.com/Simatwa/pytgpt-bot) ✨.\n"
    "For chatting, text-to-image and text-to-speech conversions.\n\n"
    "Usage commands:\n"
    "1. /start : Show this help info 📚\n"
    "2. /chat : Chat with AI 🤖\n"
    "3. /image : Generate image from text 🖼️ (default)\n"
    "4. /prodia : Generate image from text 🎨 (Prodia)\n"
    "5. /speak : Generate speech from text 🎧\n"
    "6. /intro : Set new text for chat intro 📝\n"
    "7. /voice : Set new voice for speech synthesis 🎙️\n"
    "8. /provider : Set new chat provider 🌐\n"
    "9. /awesome : Set awesome prompt as intro 💥\n"
    "10. /history : Check chat history 🕰️\n"
    "11. /check : Check current settings ⚙️\n"
    "12. /reset : Start new chat thread 🔄\n"
    "13. /myid : Echo your Telegram ID 🆔\n"
    "14. /suspend : Pause service for a while 🚫\n"
    "15. /resume : Resume paused sevice 🚀\n"
    "default : Chat with AI.\n\n"
    f"For instances {get_random_emoji('love')}:\n"
    "\t\t\t/chat Hello there.\n"
    "\t\t\t/image Peaceful desert scene\n"
    "\t\t\t/prodia Clear cool shore view\n"
    "\t\t\t/speak I am better than you.\n\n"
    f"[🌟 Star me on Github]({__repo__}) pytgpt-bot v{__version__}"
)

admin_commands = (
    "\n\nAdmin Commands\n"
    "/clear : Clear all tables 🧹\n"
    "/total : Total chats available 📊\n"
    "/drop : Delete all tables and bot logs 🗑️\n"
    "/sql : Run sql statements against database ⏳\n"
    "/logs : View bot's log 📜"
)


def handler_formatter(text: bool = False, preserve: bool = False):
    """Handles common message handler verification and execptions

    Args:
        text (bool, optional): Command must contain text?. Defaults to False.
        admin (bool, optional): Needs admin privileges?. Defaults to False.
        preserve (bool, optional): Do not alter text?. Default to False.
    """

    def main(func):

        @wraps(func)
        async def decorator(message: telebot.types.Message):
            try:
                if message.chat.type == "private":
                    logging.info(
                        f"Serving user [{get_user_id(message)}] ({message.from_user.full_name}) - Function [{func.__name__}]"
                    )
                else:
                    logging.info(f"Serving Group  - Function [{func.__name__}]")
                if not preserve:
                    message.text = telebot_util.extract_arguments(message.text)

                if text and not message.text:
                    return await bot.reply_to(
                        message,
                        f"{get_random_emoji()} Text is required❗️❗️.",
                        reply_markup=make_delete_markup(message),
                    )

                return await func(message)
            except Exception as e:
                # logging.exception(e)
                logging.error(
                    f"Error on function - {func.__name__} - {e.args[1] if e.args and len(e.args)>1 else e}"
                )
                logging.debug(str(e))
                return await bot.reply_to(
                    message,
                    text=f"{get_random_emoji('angry')} An error occured and I could't complete that request ❗️❗️❗️",
                    reply_markup=make_delete_markup(message),
                )

        return decorator

    return main


async def send_and_add_delete_button(
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
        await bot.reply_to(
            message, text=text, reply_markup=markup, parse_mode=parse_mode
        )
        if as_reply
        else await bot.send_message(
            message.chat.id, text, reply_markup=markup, parse_mode=parse_mode
        )
    )


async def send_long_text(
    message: telebot.types.Message,
    text: str,
    add_delete: bool = False,
    parse_mode: str = "Markdown",
    as_reply: bool = False,
):
    """Send texts longer than 4096 long

    Args:
        message (telebot.types.Message): Message object.
        text (str): Text to be sent.
        add_delete (bool). Add delete button. Defaults to False.
        parse_mode (str): __. Defaults to Markdown.
        as_reply (bool). Highlight the user message. Default to False.
    """
    parts: list = telebot_util.smart_split(text)
    if add_delete:
        for part in parts:
            await send_and_add_delete_button(
                message, part, parse_mode=parse_mode, as_reply=as_reply
            )
    else:
        for part in parts:
            if as_reply:
                await bot.reply_to(message, part, parse_mode=parse_mode)
            else:
                await bot.send_message(message.chat.id, part, parse_mode=parse_mode)


async def make_regenerate_and_delete_markup(
    message: telebot.types.Message, provider: str, prompt: str
) -> telebot.types.InlineKeyboardMarkup:
    """Makes a markup for deleting and regenerating images and speeches (media).

    Args:
        message (telebot.types.Message): Message object.
        provider (str): Image provider. default/prodia.
        prompt (str): text

    Returns:
        telebot.types.InlineKeyboardMarkup: Markup
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    uuid = uuid4().__str__()
    session.add(
        Temp(
            uuid=uuid,
            provider=provider,
            prompt=prompt,
        )
    )
    regenerate_button = telebot.types.InlineKeyboardButton(
        text="♻️", callback_data=f"media:{get_user_id(message,)}:{uuid}"
    )
    delete_button = telebot.types.InlineKeyboardButton(
        text="🗑️", callback_data=f"delete:{message.chat.id}:{message.id}"
    )
    markup.add(regenerate_button, delete_button)
    return markup


@bot.message_handler(commands=["help", "start"], is_chat_active=True)
@bot.channel_post_handler(commands=["help", "start"], is_chat_active=True)
@handler_formatter()
async def home(message: telebot.types.Message):
    """Show help"""
    return await bot.send_message(
        message.chat.id,
        text=(usage_info + admin_commands if User(message).is_admin else usage_info),
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["myid"], is_chat_admin=True)
@bot.channel_post_handler(commands=["myid"], is_chat_admin=True)
@handler_formatter()
async def echo_user_id(message: telebot.types.Message):
    return await bot.reply_to(
        message,
        f"Greetings {message.from_user.first_name} {get_random_emoji('love')}. Your Telegram ID is {get_user_id(message)}.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["intro"], is_chat_admin=True)
@bot.channel_post_handler(commands=["intro"], is_chat_admin=True)
@handler_formatter(text=True)
async def set_chat_intro(message: telebot.types.Message):
    """Set new value for chat intro"""
    intro = awesome_prompts_dict.get(message.text, message.text)
    if not len(intro) > 10:
        return await bot.reply_to(
            message,
            f"{get_random_emoji('angry')} The chat introduction must be at least 10 characters long.",
            reply_markup=make_delete_markup(message),
        )
    user = User(message)
    user.chat.intro = intro
    return await bot.reply_to(
        message,
        f"{get_random_emoji('happy')} New intro set successfully.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["voice"], is_chat_admin=True)
@bot.channel_post_handler(commands=["voice"], is_chat_admin=True)
@handler_formatter(text=False, preserve=True)
async def set_new_speech_voice(message: telebot.types.Message):
    """Set new voice for speech synthesis"""
    user_id: str = get_user_id(message)
    arguments: str = telebot_util.extract_arguments(message.text)
    if arguments and arguments in audio_generator.all_voices:
        User(user_id=user_id).chat.voice = arguments
        return await send_and_add_delete_button(
            message,
            f"{get_random_emoji('happy')} New voice set : `{arguments}`",
            as_reply=True,
        )

    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    make_item = lambda voice: telebot.types.InlineKeyboardButton(
        voice, callback_data=f"{voice}:{user_id}"
    )
    markup.add(*map(make_item, audio_generator.all_voices))
    await bot.delete_message(message.chat.id, message.id)
    return await bot.send_message(
        message.chat.id,
        f"Choose a voice {get_random_emoji('happy')}:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in audio_generator.all_voices
)
async def set_new_speech_voice_callback_handler(call: telebot.types.CallbackQuery):
    """Set new voice for speech synthesis callback handler"""
    await bot.delete_message(call.message.chat.id, call.message.id)
    voice, user_id = call.data.split(":")
    message = call.message
    markup = make_delete_markup(call.message)
    user = User(user_id=user_id)
    user.chat.voice = voice
    return await bot.send_message(
        message.chat.id,
        f"{get_random_emoji('happy')} New voice set : `{voice}`",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["provider"], is_chat_admin=True)
@bot.channel_post_handler(commands=["provider"], is_chat_admin=True)
@handler_formatter(text=False, preserve=True)
async def set_new_chat_provider(message: telebot.types.Message):
    """Set new text provider"""
    user_id: str = get_user_id(message)
    arguments: str = telebot_util.extract_arguments(message.text)
    if arguments and arguments in provider_keys + g4f_providers:
        User(user_id=user_id).chat.provider = arguments
        return await send_and_add_delete_button(
            message,
            f"New text provider set {get_random_emoji('love')}: `{arguments}`",
            as_reply=True,
        )
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    make_item = lambda provider: telebot.types.InlineKeyboardButton(
        provider, callback_data=f"{provider}:{user_id}"
    )
    markup.add(*map(make_item, provider_keys + g4f_providers))
    await bot.delete_message(message.chat.id, message.id)
    return await bot.send_message(
        message.chat.id,
        f"Choose a provider {get_random_emoji('love')}:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in provider_keys + g4f_providers
)
async def set_new_chat_provider_callback_handler(call: telebot.types.CallbackQuery):
    """Set new text provider callback handler"""
    await bot.delete_message(call.message.chat.id, call.message.id)
    provider, user_id = call.data.split(":")
    message = call.message
    markup = make_delete_markup(call.message)
    user = User(user_id=user_id)
    user.chat.provider = provider
    return await bot.send_message(
        message.chat.id,
        f"New text provider set {get_random_emoji('love')}: `{provider}`",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["awesome"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["awesome"], is_chat_admin=True, is_chat_active=True)
@handler_formatter(text=False, preserve=True)
async def set_awesome_prompt_as_chat_intro(message: telebot.types.Message):
    """Set awesome prompt as intro"""
    user_id: str = get_user_id(message)
    arguments: str = telebot_util.extract_arguments(message.text)
    if arguments and arguments in awesome_prompts_keys:
        new_awesome: str = awesome_prompts_dict.get(arguments)
        User(user_id=user_id).chat.intro = new_awesome
        return await send_and_add_delete_button(
            message,
            f"""New awesome-intro set:\n```{new_awesome}\n```.""",
            as_reply=True,
        )
    markup = telebot.types.InlineKeyboardMarkup(row_width=4)
    make_item = lambda awesome: telebot.types.InlineKeyboardButton(
        awesome, callback_data=f"{awesome}:{user_id}"
    )
    markup.add(*map(make_item, awesome_prompts_keys))
    await bot.delete_message(message.chat.id, message.id)
    return await bot.send_message(
        message.chat.id,
        f"Choose awesome {get_random_emoji('love')}:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in awesome_prompts_keys
)
async def set_awesome_prompt_as_chat_intro_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Set awesome prompt as intro callback handler"""
    await bot.delete_message(call.message.chat.id, call.message.id)
    awesome_prompt, user_id = call.data.split(":")
    user = User(user_id=user_id)
    user.chat.intro = awesome_prompts_dict.get(awesome_prompt)
    return await bot.send_message(
        call.message.chat.id,
        f"""New awesome-intro set:\n```{user.chat.intro}\n```.""",
        reply_markup=make_delete_markup(call.message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["check"], is_chat_admin=True)
@bot.channel_post_handler(commands=["check"], is_chat_admin=True)
@handler_formatter()
async def check_current_settings(message: telebot.types.Message):
    """Check current user settings"""
    chat = User(message).chat
    current_user_settings = (
        f"Is Active :  `{chat.is_active}`\n"
        f"Chat Length : `{len(chat.history) if chat.history else 0}`\n"
        f"Speech Voice : `{chat.voice}`\n"
        f"Chat Provider : `{chat.provider}`\n"
        f"Chat Intro : `{chat.intro}`"
    )
    return await bot.reply_to(
        message,
        current_user_settings,
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["history"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["history"], is_chat_admin=True, is_chat_active=True)
@handler_formatter()
async def check_chat_history(message: telebot.types.Message):
    user = User(message)
    return await send_long_text(
        message,
        user.chat.history or f"{get_random_emoji()} Your chat history is empty ❗️",
        add_delete=True,
        parse_mode="Markdown",
    )


async def text_to_image_default(message: telebot.types.Message):
    """Shared obj : Generate image using `image`"""
    await bot.send_chat_action(message.chat.id, "upload_photo", timeout=timeout)
    generator_obj = image_generator.AsyncImager(
        timeout=timeout,
    )
    image_chunk = await generator_obj.generate(
        message.text,
    )
    return await bot.send_photo(
        message.chat.id,
        photo=image_chunk[0],
        caption=message.text + " (default)",
        reply_markup=await make_regenerate_and_delete_markup(
            message, provider="default", prompt=message.text
        ),
    )


@bot.message_handler(commands=["image", "img"], is_chat_active=True)
@bot.channel_post_handler(commands=["image", "img"], is_chat_active=True)
@handler_formatter(text=True)
async def text_to_image_default_handler(message: telebot.types.Message):
    """Handler for image generation - default"""
    await text_to_image_default(message)


async def text_to_image_prodia(message: telebot.types.Message):
    """Shared obj : Generate image using `prodia` and respond"""
    await bot.send_chat_action(message.chat.id, "upload_photo", timeout=timeout)
    generator_obj = image_generator.AsyncProdia(timeout=timeout)
    image_chunk = await generator_obj.generate(message.text)
    return await bot.send_photo(
        message.chat.id,
        photo=image_chunk[0],
        caption=message.text + " (prodia)",
        reply_markup=await make_regenerate_and_delete_markup(
            message, provider="prodia", prompt=message.text
        ),
    )


@bot.message_handler(commands=["prodia", "prod"], is_chat_active=True)
@bot.channel_post_handler(commands=["prodia", "prod"], is_chat_active=True)
@handler_formatter(text=True)
async def text_to_image_prodia_handler(message: telebot.types.Message):
    """Handler for text to image"""
    await text_to_image_prodia(message)


async def text_to_speech(message: telebot.types.Message):
    """Shared obj : Convert text to speech and respond"""
    await bot.send_chat_action(message.chat.id, "upload_audio", timeout=timeout)
    voice = User(message).chat.voice
    audio_chunk = await audio_generator.async_text_to_audio(
        message=message.text,
        voice=voice,
        timeout=timeout,
    )
    return await bot.send_audio(
        message.chat.id,
        audio=audio_chunk,
        caption=message.text,
        reply_markup=await make_regenerate_and_delete_markup(
            message, provider="speech", prompt=message.text
        ),
        performer=voice,
        title="Text-to-Speech",
    )


@bot.message_handler(commands=["speak", "spe"], is_chat_active=True)
@bot.channel_post_handler(commands=["speak", "spe"], is_chat_active=True)
@handler_formatter(text=True)
async def text_to_speech_handler(message: telebot.types.Message):
    """Handler for text to speech"""
    await text_to_speech(message)


@bot.message_handler(commands=["reset"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["reset"], is_chat_admin=True, is_chat_active=True)
@handler_formatter()
async def reset_chat(message: telebot.types.Message):
    """Reset current chat thread"""
    user = User(message)
    session.delete(user.chat)
    return await bot.reply_to(
        message,
        f"New chat instance created. {get_random_emoji('happy')}",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["suspend"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["suspend"], is_chat_admin=True, is_chat_active=True)
@handler_formatter()
async def change_chat_status_to_inactive(message: telebot.types.Message):
    chats = User(message).chat
    chats.is_active = False
    return await bot.reply_to(
        message, text=f"Service Suspended 🚫.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["resume"], is_chat_admin=True)
@bot.channel_post_handler(commands=["resume"], is_chat_admin=True)
@handler_formatter()
async def change_chat_status_to_active(message: telebot.types.Message):
    chat = User(message).chat
    chat.is_active = True
    return await bot.reply_to(
        message, text=f"Service Resumed 🚀.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["clear", "clear_tables"], is_bot_owner=True)
@handler_formatter()
async def clear_chats(message: telebot.types.Message):
    """Delete all Tables"""
    session.query(Chat).delete()
    session.query(Temp).delete()
    logging.warning(
        f"Clearing Chats - [{message.from_user.full_name}] ({get_user_id(message)}, {message.from_user.username})"
    )
    return await bot.reply_to(
        message,
        f"{get_random_emoji('love')} Tables cleared successfully.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["total", "total_chats"], is_bot_owner=True)
@handler_formatter()
async def total_chats_query(message: telebot.types.Message):
    """Query total chats"""
    total_chats = session.query(Chat).count()
    logging.warning(
        f"Total Chats query - [{message.from_user.full_name}] ({get_user_id(message)}, {message.from_user.username})"
    )
    return await bot.reply_to(
        message,
        f"Total Chats {total_chats}",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["drop", "drop_tables"], is_bot_owner=True)
@handler_formatter()
async def total_chats_table_and_logs(message: telebot.types.Message):
    """Drop all tables and create new"""
    if logfile:
        with open(logfile, "w") as fh:
            pass
        logging.info(
            f"ADMIN CLEARED LOGS & DROPPED CHAT TABLE [{get_user_id(message)}] - ({message.from_user.full_name})\n"
        )
    logging.warning(
        f"Dropping all tables and recreate - [{message.from_user.full_name}] ({get_user_id(message)}, {message.from_user.username})"
    )
    drop_all()
    create_all()
    return await bot.reply_to(
        message,
        f"{get_random_emoji('love')} All tables dropped and logs cleared. New one created.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["sql"], is_bot_owner=True)
@handler_formatter(text=True)
async def run_sql_statement(message: telebot.types.Message):
    """Run sql statements against database"""
    logging.warning(
        f"Running SQL statements - [{message.from_user.full_name}] ({get_user_id(message)}, {message.from_user.username})"
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
        return await send_long_text(
            message,
            response,
            add_delete=True,
        )


@bot.message_handler(commands=["logs"], is_bot_owner=True)
@handler_formatter()
async def check_current_settings(message: telebot.types.Message):
    """View bot logs"""
    if not logfile:
        return await bot.reply_to(
            message,
            f"{get_random_emoji()} Logfile not specified ❗️",
            reply_markup=make_delete_markup(message),
        )
    with open(logfile, encoding="utf-8") as fh:
        contents: str = fh.read()
    return await send_long_text(message, contents, add_delete=True, parse_mode=None)


@bot.message_handler(content_types=["text"], is_chat_active=True, is_chat_command=True)
@bot.channel_post_handler(
    content_types=["text"],
    is_chat_active=True,
    commands=["chat"],
)
@handler_formatter(preserve=True)
async def text_chat(message: telebot.types.Message):
    """Text generation"""
    if telebot_util.extract_command(message.text):
        message.text = telebot_util.extract_arguments(message.text)

    user = User(message)
    conversation = Conversation(max_tokens=max_tokens)
    conversation.chat_history = user.chat.history
    conversation_prompt = conversation.gen_complete_prompt(
        message.text, intro=user.chat.intro
    )
    await bot.send_chat_action(message.chat.id, "typing")

    provider_class = provider_map.get(user.chat.provider, AsyncGPT4FREE)
    provider_class_kwargs: dict = dict(is_conversation=False, timeout=timeout)

    if user.chat.provider in g4f_providers:
        # gp4f provider
        provider_class_kwargs["provider"] = user.chat.provider

    ai_response = await provider_class(**provider_class_kwargs).chat(
        conversation_prompt
    )
    conversation.update_chat_history(
        prompt=message.text, response=ai_response, force=True
    )
    user.chat.history = conversation.chat_history
    await send_long_text(
        message, ai_response, as_reply=False if message.from_user else True
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("media:"))
async def media_regeneration_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Media regeneration callback handler"""
    action, user_id, uuid = call.data.split(":")
    message = call.message
    message.from_user.id = user_id
    temp = session.query(Temp).filter_by(uuid=uuid).first()

    if temp:
        message.text = temp.prompt
        if temp.provider == "prodia":
            return await text_to_image_prodia(message)

        elif temp.provider == "default":
            return await text_to_image_default(message)

        elif temp.provider == "speech":
            return await text_to_speech(message)
    else:
        await send_and_add_delete_button(
            message,
            f"{get_random_emoji('angry')} Cache containing that prompt was cleared!",
            as_reply=True,
        )


@bot.inline_handler(lambda query: query.query.endswith("..."))
async def handle_inline_query(inline_query: telebot.types.InlineQuery):
    """Process the inline query and return AI response"""
    try:
        user_id = get_user_id(user_id=inline_query.from_user.id)
        logging.info(f"Serving INLINE-QUERY - [{user_id}].")
        prompt = inline_query.query[:-3]
        user = User(user_id=user_id)
        conversation = Conversation(max_tokens=max_tokens)
        user_provider = provider_map.get(user.chat.provider)
        conversation_prompt = conversation.gen_complete_prompt(
            prompt, intro=user.chat.intro
        )
        ai_response = user_provider(is_conversation=False, timeout=timeout).chat(
            conversation_prompt
        )
        feedback_options = [
            telebot.types.InlineQueryResultArticle(
                id="1",
                title=ai_response,  # "AI Generated",
                input_message_content=telebot.types.InputTextMessageContent(
                    ai_response
                ),
            )
        ]
        await bot.answer_inline_query(inline_query.id, feedback_options)

    except Exception as e:
        logging.debug(f"Error while handling inline query - [{user_id}]. {e}")
        logging.error(
            f"Error while handling inline query - [{user_id}] : {e.args[1] if e.args and len(e.args)>1 else e}"
        )


@bot.message_handler(is_chat_active=True)
@bot.channel_post_handler(is_chat_active=True, is_bot_tagged=True)
async def any_other_action(message):
    return await bot.reply_to(
        message,
        usage_info,
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete:"))
async def delete_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Delete callback handler"""
    action, trigger_chat_id, trigger_message_id = call.data.split(":")
    try:
        await bot.delete_message(trigger_chat_id, trigger_message_id)
    except:
        pass
    try:
        await bot.delete_message(call.message.chat.id, call.message.id)
    except:
        pass


bot.add_custom_filter(IsBotOwnerFilter())
bot.add_custom_filter(IsAdminFilter(bot))
bot.add_custom_filter(IsActiveFilter())
bot.add_custom_filter(IsBotTaggedFilter(loop.run_until_complete(bot.get_me())))
bot.add_custom_filter(IsChatCommandFilter())
