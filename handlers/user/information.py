from aiogram import types, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dispatcher import dp, bot
from messages import Messages


def getinformationkeyboard():
    keyboard = InlineKeyboardBuilder()
    for i in Messages.infobuttonswithlinks:
        keyboard.add(InlineKeyboardButton(text=i[0], url=i[1]))
    return keyboard.as_markup(resize_keyboard=True)


@dp.message(F.text == "⚙️ Информация")
async def inform(message: types.Message):
    await bot.send_message(message.from_user.id, Messages.information, reply_markup=getinformationkeyboard())
