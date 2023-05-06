"""
    Callbacks to handling buttons.
"""

import uuid

from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import find_first_between
from user import get_current_user
from dict_processor import DictProcessor

dt = DictProcessor()


async def send_message_middleware(bot: Bot, chat_id: int, message: str):
    await bot.send_message(chat_id, text=message)


async def handle_examples_callback(call: CallbackQuery, bot: Bot, apscheduler: AsyncIOScheduler):
    res, ts = dt.get_dict_examples(find_first_between(call.message.md_text, "*", "*"))
    await bot.send_message(call.from_user.id, res)
    await call.answer()


async def handle_repeat_callback(call: CallbackQuery, bot: Bot, apscheduler: AsyncIOScheduler):
    current_user_id = call.from_user.id
    current_user = get_current_user(current_user_id)

    for timing in current_user.timings_repeat:
        target_word = find_first_between(call.message.md_text, "*", "*")
        apscheduler.add_job(
            id=target_word + "_" + str(call.message.chat.id) + '_' + uuid.uuid1().__str__(),
            func=send_message_middleware,
            trigger='date',
            run_date=datetime.now() + timedelta(minutes=timing),
            kwargs={"bot": bot, "chat_id": call.message.chat.id, "message": call.message.md_text})
    await call.answer('Word added to your reminder', show_alert=True)


async def callback_handler(call: CallbackQuery, bot: Bot, apscheduler: AsyncIOScheduler):
    if call.data == 'callback_examples':
        await handle_examples_callback(call=call, bot=bot, apscheduler=apscheduler)
    if call.data == 'callback_repeat':
        await handle_repeat_callback(call=call, bot=bot, apscheduler=apscheduler)
