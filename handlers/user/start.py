from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from dispatcher import dp, bot
from messages import Messages


def getstartkeyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.row(KeyboardButton(text="👨‍💻 Профиль"))
    keyboard.row(KeyboardButton(text="⚙️ Информация"))
    keyboard.row(KeyboardButton(text="🔨 Билд"))
    return keyboard.as_markup(resize_keyboard=True)


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(message.from_user.id, text=Messages.start_message, reply_markup=getstartkeyboard())
