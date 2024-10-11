from typing import Union

import arrow
from aiogram.filters import Filter
from aiogram.types import Message

import config
from models.models import User


class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in config.admins_ids:
            return True
        else:
            return False


class IsSub(Filter):
    async def __call__(self, message: Message, user: User) -> bool:
        timesub = arrow.get(user.subuntil)
        if timesub > arrow.now("Europe/Moscow"):
            return True
        else:
            return False


class ChatTypeFilter(Filter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
