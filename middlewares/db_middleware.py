from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update

from dbworker import get_user, add_user
from utils.utils import send_admins


class DBMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]
    ) -> Any:
        if event.message:
            from_user = event.message.from_user
        elif event.callback_query:
            from_user = event.callback_query.from_user
        else:
            return await handler(event, data)

        if from_user.is_bot:
            return await handler(event, data)

        user = await get_user(from_user.id)

        newuser = False
        if user is None:
            user = await add_user(from_user.id)
            newuser = True

        if user.banstatus:
            return

        data["user"] = user

        if from_user.username is not None:
            if user is not None:
                if user.username != "@" + from_user.username:
                    user.username = "@" + from_user.username
                    await user.save()

        await handler(event, data)
        if newuser:
            msg = ""
            if from_user.username:
                msg = f" <b>|</b> @{from_user.username}"
            await send_admins(event.bot, f"<b>👨В боте зарегистрирован новый пользователь</b>: <code>{from_user.id}</code>" + msg)
