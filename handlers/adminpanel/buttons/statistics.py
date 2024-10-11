import arrow
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from dbworker import get_all_purchases
from dispatcher import dp
from handlers.adminpanel.adminpanel import back_to_admin_keyboard


@dp.callback_query(F.data == "statistics")
async def process_callback_button1(callback_query: types.CallbackQuery):
    purchases = await get_all_purchases()

    suballtimesum = 0
    zalivalltimesum = 0
    subtodaysum = 0
    zalivtodaysum = 0
    suballtime = 0
    zalivalltime = 0
    subtoday = 0
    zalivtoday = 0
    for i in purchases:
        if i.type == "sub":
            suballtimesum += i.sum
            suballtime += 1
            if arrow.get(i.date).date() == arrow.now("Europe/Moscow").date():
                subtodaysum += i.sum
                subtoday += 1

    text = ("<b>За всё время:</b>\n"
            f"<b>Подписки</b>: <code>{suballtimesum}</code>₽ <b>({suballtime} шт)</b>\n"
            f"<b>Заливы</b>: <code>{zalivalltimesum}</code>₽ <b>({zalivalltime} шт)</b>\n\n"
            f"<b>За сегодня:</b>\n"
            f"<b>Подписки</b>: <code>{subtodaysum}</code>₽ <b>({subtoday} шт)</b>\n"
            f"<b>Заливы</b>: <code>{zalivtodaysum}</code>₽ <b>({zalivtoday} шт)</b>\n\n")
    await callback_query.message.edit_text(text, reply_markup=back_to_admin_keyboard())