"""
    Buttons for Telegram bot.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

repeat_menu = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Examples', callback_data='callback_examples')
        ],
        [
            InlineKeyboardButton(text='Repeat Word', callback_data='callback_repeat')
        ]
    ]
)