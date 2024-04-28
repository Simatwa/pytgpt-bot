import telebot
import json
import logging
import telebot.util as telebot_util
import pytgpt.imager as image_generator
from pytgpt.utils import Audio as audio_generator
from pytgpt.utils import Conversation
from pytgpt.utils import AwesomePrompts
from functools import wraps
from sqlalchemy import text

from pytgpt_bot import __version__, __repo__

from pytgpt_bot.config import (
    bot_token,
    max_tokens,
    timeout,
    loglevel,
    logfile,
    admin_ids,
    provider,
)
from pytgpt_bot.db import User
from pytgpt_bot.utils import (
    provider_keys,
    get_random_emoji,
    provider_map,
    make_delete_markup,
    make_regenerate_and_delete_markup,
)
from pytgpt_bot.models import session, Chat, create_all, drop_all
from pytgpt_bot.filters import (
    IsActiveFilter,
    IsBotOwnerFilter,
    IsAdminFilter,
    IsBotTaggedFilter,
    IsChatCommandFilter,
)

chosen_provider: str = provider_map.get(provider)

log_params = dict(
    format="%(asctime)s : %(levelname)s - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
    level=loglevel,
)

awesome_prompts_dict: dict = AwesomePrompts().get_acts()
awesome_prompts_keys: list = list(awesome_prompts_dict.keys())

if logfile:
    log_params["filename"] = logfile

logging.basicConfig(**log_params)

bot = telebot.TeleBot(bot_token, disable_web_page_preview=True)

bot.remove_webhook()

logging.info(
    f"Bot started sucessfully {get_random_emoji('happy')}. Admin IDs - [{', '.join(admin_ids)}]"
)

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
    "/clear : Clear all chats 🧹\n"
    "/total : Total chats available 📊\n"
    "/drop : Clear entire chat table and bot logs 🗑️\n"
    "/sql : Run sql statements against database ⏳\n"
    "/logs : View bot logs 📜"
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
        def decorator(message: telebot.types.Message):
            try:
                if message.chat.type == "private":
                    logging.info(
                        f"Serving user [{message.from_user.id}] ({message.from_user.full_name}) - Function [{func.__name__}]"
                    )
                else:
                    logging.info(f"Serving Group  - Function [{func.__name__}]")
                if not preserve:
                    message.text = telebot_util.extract_arguments(message.text)

                if text and not message.text:
                    return bot.reply_to(
                        message,
                        f"{get_random_emoji()} Text is required❗️❗️.",
                        reply_markup=make_delete_markup(message),
                    )

                return func(message)
            except Exception as e:
                # logging.exception(e)
                logging.error(
                    f"Error on function - {func.__name__} - {e.args[1] if e.args and len(e.args)>1 else e}"
                )
                logging.debug(str(e))
                bot.reply_to(
                    message,
                    text=f"{get_random_emoji('angry')} An error occured and I could't complete that request ❗️❗️❗️",
                    reply_markup=make_delete_markup(message),
                )

        return decorator

    return main


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
            send_and_add_delete_button(
                message, part, parse_mode=parse_mode, as_reply=as_reply
            )
    else:
        for part in parts:
            if as_reply:
                bot.reply_to(message, part, parse_mode=parse_mode)
            else:
                bot.send_message(message.chat.id, part, parse_mode=parse_mode)


@bot.message_handler(commands=["help", "start"], is_chat_active=True)
@bot.channel_post_handler(commands=["help", "start"], is_chat_active=True)
@handler_formatter()
def home(message: telebot.types.Message):
    """Show help"""
    # print(message)
    return bot.send_message(
        message.chat.id,
        text=(usage_info + admin_commands if User(message).is_admin else usage_info),
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["myid"], is_chat_admin=True)
@bot.channel_post_handler(commands=["myid"], is_chat_admin=True)
@handler_formatter()
def echo_user_id(message: telebot.types.Message):
    return bot.reply_to(
        message,
        f"Greetings {message.from_user.first_name} {get_random_emoji('love')}. Your Telegram ID is {message.from_user.id}.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["intro"], is_chat_admin=True)
@bot.channel_post_handler(commands=["intro"], is_chat_admin=True)
@handler_formatter(text=True)
def set_chat_intro(message: telebot.types.Message):
    """Set new value for chat intro"""
    intro = awesome_prompts_dict.get(message.text, message.text)
    if not len(intro) > 10:
        return bot.reply_to(
            message,
            f"{get_random_emoji('sad')} The chat introduction must be at least 10 characters long.",
            reply_markup=make_delete_markup(message),
        )
    user = User(message)
    user.chat.intro = intro
    return bot.reply_to(
        message, "New intro set successfully.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["voice"], is_chat_admin=True)
@bot.channel_post_handler(commands=["voice"], is_chat_admin=True)
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
    return bot.send_message(
        message.chat.id,
        f"Choose a voice {get_random_emoji('happy')}:",
        reply_markup=markup,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.split(":")[0] in audio_generator.all_voices
)
def set_new_speech_voice_callback_handler(call: telebot.types.CallbackQuery):
    """Set new voice for speech synthesis callback handler"""
    bot.delete_message(call.message.chat.id, call.message.id)
    voice, user_id = call.data.split(":")
    message = call.message
    markup = make_delete_markup(call.message)
    user = User(user_id=int(user_id))
    user.chat.voice = voice
    return bot.send_message(
        message.chat.id,
        f"{get_random_emoji('happy')} New voice set : `{voice}`",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["provider"], is_chat_admin=True)
@bot.channel_post_handler(commands=["provider"], is_chat_admin=True)
@handler_formatter(text=False)
def set_new_chat_provider(message: telebot.types.Message):
    """Set new text provider"""
    user_id: str = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    make_item = lambda provider: telebot.types.InlineKeyboardButton(
        provider, callback_data=f"{provider}:{user_id}"
    )
    markup.add(*map(make_item, provider_keys))
    bot.delete_message(message.chat.id, message.id)
    return bot.send_message(
        message.chat.id,
        f"Choose a provider {get_random_emoji('love')}:",
        reply_markup=markup,
    )


@bot.callback_query_handler(func=lambda call: call.data.split(":")[0] in provider_keys)
def set_new_chat_provider_callback_handler(call: telebot.types.CallbackQuery):
    """Set new text provider callback handler"""
    bot.delete_message(call.message.chat.id, call.message.id)
    provider, user_id = call.data.split(":")
    message = call.message
    markup = make_delete_markup(call.message)
    user = User(user_id=int(user_id))
    user.chat.provider = provider
    return bot.send_message(
        message.chat.id,
        f"New text provider set {get_random_emoji('love')}: `{provider}`",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["awesome"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["awesome"], is_chat_admin=True, is_chat_active=True)
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
    return bot.send_message(
        message.chat.id,
        f"Choose awesome {get_random_emoji('love')}:",
        reply_markup=markup,
    )


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
    user.chat.intro = awesome_prompts_dict.get(awesome_prompt)
    return bot.send_message(
        call.message.chat.id,
        f"""New awesome-intro set:\n```{user.chat.intro}\n```.""",
        reply_markup=make_delete_markup(call.message),
        parse_mode="Markdown",
    )


@bot.message_handler(commands=["check"], is_chat_admin=True)
@bot.channel_post_handler(commands=["check"], is_chat_admin=True)
@handler_formatter()
def check_current_settings(message: telebot.types.Message):
    """Check current user settings"""
    chat = User(message).chat
    current_user_settings = (
        f"Is Active :  `{chat.is_active}`\n"
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


@bot.message_handler(commands=["history"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["history"], is_chat_admin=True, is_chat_active=True)
@handler_formatter()
def check_chat_history(message: telebot.types.Message):
    user = User(message)
    return send_long_text(
        message,
        user.chat.history or f"{get_random_emoji()} Your chat history is empty ❗️",
        add_delete=True,
        parse_mode="Markdown",
    )


def text_to_image_default(message: telebot.types.Message):
    """Shared obj : Generate image using `image`"""
    bot.send_chat_action(message.chat.id, "upload_photo", timeout=timeout)
    generator_obj = image_generator.Imager(
        timeout=timeout,
    )
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(
            message.text,
        )[0],
        caption=message.text + " (default)",
        reply_markup=make_regenerate_and_delete_markup(
            message, provider="default", prompt=message.text
        ),
    )


@bot.message_handler(commands=["image", "img"], is_chat_active=True)
@bot.channel_post_handler(commands=["image", "img"], is_chat_active=True)
@handler_formatter(text=True)
def text_to_image_default_handler(message: telebot.types.Message):
    """Handler for image generation - default"""
    text_to_image_default(message)


def text_to_image_prodia(message: telebot.types.Message):
    """Shared obj : Generate image using `prodia` and respond"""
    bot.send_chat_action(message.chat.id, "upload_photo", timeout=timeout)
    generator_obj = image_generator.Prodia(timeout=timeout)
    return bot.send_photo(
        message.chat.id,
        photo=generator_obj.generate(message.text)[0],
        caption=message.text + " (prodia)",
        reply_markup=make_regenerate_and_delete_markup(
            message, provider="prodia", prompt=message.text
        ),
    )


@bot.message_handler(commands=["prodia", "prod"], is_chat_active=True)
@bot.channel_post_handler(commands=["prodia", "prod"], is_chat_active=True)
@handler_formatter(text=True)
def text_to_image_prodia_handler(message: telebot.types.Message):
    """Handler for text to image"""
    text_to_image_prodia(message)


def text_to_speech(message: telebot.types.Message):
    """Shared obj : Convert text to speech and respond"""
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
        reply_markup=make_regenerate_and_delete_markup(
            message, provider="speech", prompt=message.text
        ),
        performer=voice,
        title="Text-to-Speech",
    )


@bot.message_handler(commands=["speak", "spe"], is_chat_active=True)
@bot.channel_post_handler(commands=["speak", "spe"], is_chat_active=True)
@handler_formatter(text=True)
def text_to_speech_handler(message: telebot.types.Message):
    """Handler for text to speech"""
    text_to_speech(message)


@bot.message_handler(commands=["reset"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["reset"], is_chat_admin=True, is_chat_active=True)
@handler_formatter()
def reset_chat(message: telebot.types.Message):
    """Reset current chat thread"""
    user = User(message)
    user.delete()
    return bot.reply_to(
        message,
        f"New chat instance created. {get_random_emoji('happy')}",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["suspend"], is_chat_admin=True, is_chat_active=True)
@bot.channel_post_handler(commands=["suspend"], is_chat_admin=True, is_chat_active=True)
@handler_formatter()
def change_chat_status_to_inactive(message: telebot.types.Message):
    chats = User(message).chat
    chats.is_active = False
    return bot.reply_to(
        message, text=f"Service Suspended 🚫.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["resume"], is_chat_admin=True)
@bot.channel_post_handler(commands=["resume"], is_chat_admin=True)
@handler_formatter()
def change_chat_status_to_active(message: telebot.types.Message):
    chat = User(message).chat
    chat.is_active = True
    return bot.reply_to(
        message, text=f"Service Resumed 🚀.", reply_markup=make_delete_markup(message)
    )


@bot.message_handler(commands=["clear", "clear_chats"], is_bot_owner=True)
@handler_formatter()
def clear_chats(message: telebot.types.Message):
    """Delete all chat entries"""
    session.query(Chat).delete()
    logging.warning(
        f"Clearing Chats - [{message.from_user.full_name}] ({message.from_user.id}, {message.from_user.username})"
    )
    return bot.reply_to(
        message,
        f"{get_random_emoji('love')} Chats cleared successfully.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["total", "total_chats"], is_bot_owner=True)
@handler_formatter()
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


@bot.message_handler(commands=["drop", "drop_chats"], is_bot_owner=True)
@handler_formatter()
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
        f"{get_random_emoji('love')} Chat table and bot logs dropped and new one created.",
        reply_markup=make_delete_markup(message),
    )


@bot.message_handler(commands=["sql"], is_bot_owner=True)
@handler_formatter(text=True)
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


@bot.message_handler(commands=["logs"], is_bot_owner=True)
@handler_formatter()
def check_current_settings(message: telebot.types.Message):
    """View bot logs"""
    if not logfile:
        return bot.reply_to(
            message,
            f"{get_random_emoji()} Logfile not specified ❗️",
            reply_markup=make_delete_markup(message),
        )
    with open(logfile, encoding="utf-8") as fh:
        contents: str = fh.read()
    return send_long_text(message, contents, add_delete=True, parse_mode=None)


@bot.message_handler(content_types=["text"], is_chat_active=True, is_chat_command=True)
@bot.channel_post_handler(
    content_types=["text"],
    is_chat_active=True,
    commands=["chat"],
)
@handler_formatter()
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
    send_long_text(message, ai_response, as_reply=False if message.from_user else True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("media::"))
def media_regeneration_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Media regeneration callback handler"""
    action, provider, prompt = call.data.split("::")
    message = call.message
    message.text = prompt
    if provider == "prodia":
        return text_to_image_prodia(message)
    elif provider == "default":
        return text_to_image_default(message)
    elif provider == "speech":
        return text_to_speech(message)


@bot.inline_handler(lambda query: query.query.endswith("..."))
def handle_inline_query(inline_query: telebot.types.InlineQuery):
    """Process the inline query and return AI response"""
    try:
        logging.info("Serving INLINE-QUERY - [{inline_query.from_user.id}].")
        prompt = inline_query.query[:-3]
        user = User(user_id=inline_query.from_user.id)
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
        bot.answer_inline_query(inline_query.id, feedback_options)

    except Exception as e:
        logging.debug(
            f"Error while handling inline query - [{inline_query.from_user.id}]. {e}"
        )
        logging.error(
            f"Error while handling inline query - [{inline_query.from_user.id}] : {e.args[1] if e.args and len(e.args)>1 else e}"
        )


@bot.message_handler(is_chat_active=True)
@bot.channel_post_handler(is_chat_active=True, is_bot_tagged=True)
def any_other_action(message):
    return bot.reply_to(
        message,
        usage_info,
        reply_markup=make_delete_markup(message),
        parse_mode="Markdown",
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete::"))
def delete_callback_handler(
    call: telebot.types.CallbackQuery,
):
    """Delete callback handler"""
    action, trigger_chat_id, trigger_message_id = call.data.split("::")
    try:
        bot.delete_message(trigger_chat_id, trigger_message_id)
    except:
        pass
    try:
        bot.delete_message(call.message.chat.id, call.message.id)
    except:
        pass


bot.add_custom_filter(IsBotOwnerFilter())
bot.add_custom_filter(IsAdminFilter(bot))
bot.add_custom_filter(IsActiveFilter())
bot.add_custom_filter(IsBotTaggedFilter(bot.get_me()))
bot.add_custom_filter(IsChatCommandFilter())
