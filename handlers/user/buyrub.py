import asyncio
import traceback

from aiogram import types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from dispatcher import dp, bot
from models.models import User
from utils.crystalpay import AIOCrystalPay
from utils.utils import cancelkeyboard

crystal = AIOCrystalPay(config.login, config.secret1)


class CrystalData(CallbackData, prefix="cd"):
    amount: int

class CrystalCheckData(CallbackData, prefix="cch"):
    id: str
    amount: int


class RubBuy(StatesGroup):
    ammount = State()


@dp.callback_query(F.data == "buyrub")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()
    await bot.send_message(chat_id=callback_query.from_user.id, text="👩‍🔬 <b>Введите кол-во $ для пополнения.</b>\n",
                           reply_markup=cancelkeyboard())
    await state.set_state(RubBuy.ammount)


@dp.message(RubBuy.ammount)
async def inform(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await bot.send_message(message.from_user.id, "❌<b>Это не число.</b>")
        return
    if int(message.text) < 1:
        await bot.send_message(message.from_user.id, "❌<b>Минимальная сумма для пополнения</b>: <code>1</code> $")
        return
    if int(message.text) > 10000:
        await bot.send_message(message.from_user.id, "❌<b>Максимальная сумма для пополнения</b>: <code>10000</code> $")
        return

    money = int(message.text)

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='🔹 CrystalPAY', callback_data=CrystalData(amount=money).pack()))
    kb = kb.as_markup()
    await bot.send_message(chat_id=message.from_user.id, text="💵 <b>Выберите способ оплаты</b>", reply_markup=kb)
    await state.clear()


@dp.callback_query(CrystalData.filter())
async def inform(callback_query: types.CallbackQuery, callback_data: CrystalData):
    amount = callback_data.amount
    try:
        payment = await crystal.create_invoice(amount=int(amount), lifetime=30, redirect_url=config.bot_url, currency="USD")
        await payment.get_amount()
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text="Оплатить", url=payment.url))
        kb.add(InlineKeyboardButton(text="✅ Проверить оплату", callback_data=CrystalCheckData(id=payment.id, amount=amount).pack()))
        kb = kb.as_markup()

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=f"📝 <b>Счет на оплату</b>\n\n"
                                         f"🆔 <b>Номер</b>: <code>{payment.id}</code>\n"
                                         f"💸 <b>Сумма</b>: <code>{payment.amount}</code> RUB\n"
                                         f"🕰 <b>Время на оплату</b>: <b>30 минут</b>",
                                    reply_markup=kb)

    except Exception as e:
        traceback.print_exc()
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=f"Возникла ошибка")


@dp.callback_query(CrystalCheckData.filter())
async def inform(callback_query: types.CallbackQuery, callback_data: CrystalCheckData, user: User):
    paymentid = callback_data.id
    amount = callback_data.amount

    async with asyncio.Lock():
        try:
            payment = await crystal.construct_payment_by_id(paymentid)

            if await payment.is_paid():
                await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            text=f"💳 <b>Вам было начислено <code>{amount}</code> $!</b>")
                user.balance += int(amount)
                await user.save()
            else:
                await bot.answer_callback_query(callback_query.id, text="Счёт не оплачен!")
        except Exception as e:
            traceback.print_exc()
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=f"Возникла ошибка")



