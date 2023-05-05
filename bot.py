#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

import logging

from telegram import *
from telegram.ext import *

from dict_processor import DictProcessor

dict_processor = DictProcessor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends explanation on how to use the bot.
    """
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send the alarm message.
    """
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Remove job with given name. Returns whether job was removed.
    """
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add a job to the queue.
    """
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Remove the job if the user changed their mind.
    """
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def message_handler(update: Update, context: CallbackContext) -> None:
    """
    Echo the user message.
    """
    word = update.message.text
    res = dict_processor.get_dict_examples(word)
    await update.message.reply_text(res, parse_mode='MarkdownV2')

    buttons = [[InlineKeyboardButton("yes", callback_data="like")], [InlineKeyboardButton("no", callback_data="dislike")]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_markup=InlineKeyboardMarkup(buttons), text="Did you like the image?")


def queryHandler(update: Update, context: CallbackContext):
    query = update.callback_query.data
    update.callback_query.answer()

    global likes, dislikes

    if "like" in query:
        likes += 1

    if "dislike" in query:
        dislikes += 1

    print(f"likes => {likes} and dislikes => {dislikes}")

def main() -> None:
    """
    Run bot.
    """
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6064845576:AAG03rHT1wyqdUlBtHbyovC5V2kwLV_fSE0").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CallbackQueryHandler(queryHandler))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()