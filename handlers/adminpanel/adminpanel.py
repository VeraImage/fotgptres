from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from dispatcher import bot, dp
from handlers.filters import IsAdmin
from handlers.user.profile import profilemsg, profilekb
from models.models import User


async def getadminpanelkeyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Сделать рассылку📢", callback_data="mailing"))
    keyboard.row(InlineKeyboardButton(text="Редактировать пользователя ✍", callback_data="editprofile"))
    keyboard.row(InlineKeyboardButton(text="Статистика 📊", callback_data="statistics"))
    keyboard.row(InlineKeyboardButton(text="Назад🔙", callback_data="adminback"))
    return keyboard.as_markup(resize_keyboard=True)


def back_to_admin_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="backtoadmin"))
    return kb.as_markup()


@dp.callback_query(IsAdmin(), F.data == "adminpanel")
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        "⚙️ <b>Админ панель</b>",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=await getadminpanelkeyboard(),
    )


@dp.callback_query(F.data == "adminback")
async def process_callback_button1(callback_query: types.CallbackQuery, user: User):
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        text=profilemsg(callback_query.from_user.full_name, user),
        reply_markup=profilekb(user.tgid in config.admins_ids),
        message_id=callback_query.message.message_id,
    )


@dp.callback_query(F.data == "backtoadmin")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        "⚙️ <b>Админ панель</b>",
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=await getadminpanelkeyboard(),
    )