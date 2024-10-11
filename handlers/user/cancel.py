from aiogram import F, types
from aiogram.fsm.context import FSMContext

from dispatcher import dp


@dp.callback_query(F.data == "cancelinline")
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("<b>👍 Отменено.</b>")