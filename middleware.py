"""
    Middleware for telegram bot.
"""

from aiogram import BaseMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Dict, Any, Callable, Awaitable
from aiogram.types.base import TelegramObject


class SchedulerMiddleware(BaseMiddleware):
    def __init__(self, scheduler: AsyncIOScheduler):
        super().__init__()
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]) -> Any:
        data["apscheduler"] = self.scheduler
        return await handler(event, data)