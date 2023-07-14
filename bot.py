"""
    Telegram bot code with handlers and middleware.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InputMediaPhoto, FSInputFile

from buttons import repeat_menu
from dict_processor import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middleware import SchedulerMiddleware
from callbacks import callback_handler
from commands import set_commands
from utils import find_first_between
from user import get_current_user, users

dt = DictProcessor()
dp = Dispatcher()


@dp.message(Command("timings"))
async def command_transcription_handle(message: Message, bot: Bot) -> None:
    user = get_current_user(message.from_user.id)
    if len(message.text.split(" ")) == 1:
        await bot.send_message(message.chat.id,
           text="Yur current timing: each {} minutes\.".format(user.timings_repeat))
        return

    if not user.edited:
        timings_int = [int(time) for time in message.text.split(" ")[1:]]
        user.set_timings(timings_int)
        user.id = message.from_user.id
        users.append(user)
    await bot.send_message(message.chat.id, text="Timings setted\.")


@dp.message(Command("transcription"))
async def command_transcription_handle(message: Message, bot: Bot) -> None:
    ts_image = InputMediaPhoto(type='photo', media=FSInputFile("images/en-transcription.jpg"))
    await bot.send_media_group(message.chat.id, [ts_image])


@dp.message(Command("remove"))
async def command_start_handle(message: Message, bot: Bot, apscheduler: AsyncIOScheduler) -> None:
    word = message.text.split(" ")[1:]
    delete_all = False
    if not len(word):
        await bot.send_message(message.chat.id, text="Use key `/remove <word>` or `/remove all`\.")
        return
    if ' '.join(word) == 'all':
        for job in apscheduler.get_jobs():
            id_word, id_chat, id_uuid = job.id.split('_')
            if int(id_chat) == message.chat.id:
                delete_all = True
                apscheduler.remove_job(job.id)
        if delete_all:
            await bot.send_message(message.chat.id, text="Removed all words from reminder\.")
        else:
            await bot.send_message(message.chat.id, text="No words in your reminder\.")
        return

    delete_word = False
    for job in apscheduler.get_jobs():
        id_word, id_chat, id_uuid = job.id.split('_')
        if id_word == ' '.join(word) and int(id_chat) == message.chat.id:
            delete_word = True
            apscheduler.remove_job(job.id)
    if delete_word:
        await bot.send_message(message.chat.id, text="Word *{}* removed from reminder\.".format(' '.join(word)))
    else:
        await bot.send_message(message.chat.id, text="Word *{}* doesn't exist in the reminder\.".format(' '.join(word)))


@dp.message(Command("show"))
async def command_show_handle(message: Message, bot: Bot, apscheduler: AsyncIOScheduler) -> None:
    res_words = []
    for job in apscheduler.get_jobs():
        id_word, id_chat, id_uuid = job.id.split('_')
        trans_list = find_first_between(job.kwargs['message'], '_', '_').replace('\r', '')
        if int(id_chat) == message.chat.id:
            res_words.append('*' + id_word + '*' + ': ' + trans_list)
    if not len(res_words):
        await bot.send_message(message.chat.id, text="No words in your reminder\.")
    res_words = set(res_words)
    res_md = ''
    for i, word in enumerate(res_words):
        text = str(i) + '\. _' + word + '_\n\n'
        res_md += text
    await bot.send_message(message.chat.id, text=res_md)



@dp.message()
async def handle_message(message: Message) -> None:
    res, ts = dt.get_dict(message.text)
    if not res:
        await message.answer("Cannot recognize word\.")
    await message.answer(res, reply_markup=repeat_menu)


async def main() -> None:

    bot = Bot(token="6064845576:AAG03rHT1wyqdUlBtHbyovC5V2kwLV_fSE0", parse_mode='MarkdownV2')

    await set_commands(bot)

    dp.callback_query.register(callback_handler)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    dp.update.middleware.register(SchedulerMiddleware(scheduler=scheduler))

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    # await main()