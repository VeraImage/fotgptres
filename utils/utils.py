from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config


async def send_admins(bot: Bot, message):
    for i in config.admins_ids:
        await bot.send_message(i, message)


def cancelkeyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❎ Отменить", callback_data="cancelinline"))
    return keyboard.as_markup(resize_keyboard=True)
