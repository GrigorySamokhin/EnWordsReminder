from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='transcription',
            description='Show transcription image'
        ),
        BotCommand(
            command='remove',
            description='Delete given word from reminders. Example /remove "insist"'
        ),
        BotCommand(
            command='show',
            description='Shows all words in your reminder'
        ),
        BotCommand(
            command='timings',
            description='Set timings for your reminder. Example /timings 40 120 380 ... 1240'
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())