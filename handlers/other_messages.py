from aiogram import types
from aiogram.fsm.context import FSMContext

from dispatcher import dp
from handlers.filters import ChatTypeFilter


@dp.message(ChatTypeFilter(chat_type=["private"]))
async def processing_missed_messages(message: types.Message, state: FSMContext):
    await message.answer("❌ <b>Неизвестная команда.\nВведите /start</b>")
