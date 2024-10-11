import arrow

import config
from dbworker import add_purchase
from models.models import User
from aiogram import F, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dispatcher import dp


def subs_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=f"📆 30 дней | {config.price[30]}$", callback_data="buysubdays_30"))
    kb.row(InlineKeyboardButton(text=f"📆 90 дней | {config.price[30]}$", callback_data="buysubdays_90"))
    kb.row(InlineKeyboardButton(text=f"📆 360 дней | {config.price[30]}$", callback_data="buysubdays_360"))
    kb.row(InlineKeyboardButton(text=f"🏆 PRO 30 дней | {config.proprice[30]}$", callback_data="buyprosubdays_30"))
    kb.row(InlineKeyboardButton(text=f"🏆 PRO 90 дней | {config.proprice[90]}$", callback_data="buyprosubdays_90"))
    kb.row(InlineKeyboardButton(text=f"🏆 PRO 360 дней | {config.proprice[360]}$", callback_data="buyprosubdays_360"))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="adminback"))
    return kb.as_markup()


@dp.callback_query(F.data == "buysub")
async def process(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "📅 <b>Выберите длительность подписки:</b>\n\n"
        "🔄 <i>Если у вас уже есть активная подписка, её срок будет продлен.</i>\n",
        reply_markup=subs_keyboard()
    )


@dp.callback_query(F.data.startswith("buysubdays"))
async def process(callback_query: types.CallbackQuery, user: User):
    subdays = int(callback_query.data.split("_")[1])
    price = config.price[subdays]
    if user.balance >= price:
        if arrow.get(user.subuntil) < arrow.now("Europe/Moscow"):
            user.subuntil = arrow.now("Europe/Moscow").shift(days=subdays).datetime
            await user.save()
        else:
            user.subuntil = arrow.get(user.subuntil).shift(days=subdays).datetime

        user.subfrom = arrow.now("Europe/Moscow").datetime
        user.balance -= price
        await user.save()
        await callback_query.answer(
            show_alert=True, 
            text="✅ Успешно!"
        )
        await add_purchase("sub", price, callback_query.from_user.id, arrow.now("Europe/Moscow").datetime)
    else:
        await callback_query.answer(
            show_alert=True, 
            text="❌ Недостаточно средств!"
        )

@dp.callback_query(F.data.startswith("buyprosubdays"))
async def process(callback_query: types.CallbackQuery, user: User):
    subdays = int(callback_query.data.split("_")[1])
    price = config.proprice[subdays]
    if user.balance >= price:
        if arrow.get(user.prosubuntil) < arrow.now("Europe/Moscow"):
            user.prosubuntil = arrow.now("Europe/Moscow").shift(days=subdays).datetime
            await user.save()
        else:
            user.prosubuntil = arrow.get(user.prosubuntil).shift(days=subdays).datetime

        user.balance -= price
        await user.save()
        await callback_query.answer(
            show_alert=True, 
            text="✅ Успешно!"
        )
        await add_purchase("prosub", price, callback_query.from_user.id, arrow.now("Europe/Moscow").datetime)
    else:
        await callback_query.answer(
            show_alert=True, 
            text="❌ Недостаточно средств!"
        )

