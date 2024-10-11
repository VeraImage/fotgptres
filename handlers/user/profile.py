import arrow
from aiogram import html
from aiogram import types, F
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from dispatcher import dp, bot
from models.models import User


def profilemsg(name, user: User):
    timesub = arrow.get(user.subuntil)
    protimesub = arrow.get(user.prosubuntil)

    if timesub > arrow.now("Europe/Moscow"):
        subhours = str(int(((timesub - arrow.now("Europe/Moscow")).total_seconds() / 60 /60)))
    else:
        subhours = "отсутствует"

    if protimesub > arrow.now("Europe/Moscow"):
        prosubhours = str(int(((protimesub - arrow.now("Europe/Moscow")).total_seconds() / 60 /60)))
    else:
        prosubhours = "отсутствует"
    msg = f"🙋<b>Здравствуйте, <code>{html.quote(name)}</code>\n\n" f"👨‍💻 Профиль</b>\n\n🆔 <b>Ваш айди:</b> <code>{user.tgid}</code> \n💸 <b>Баланс</b>: <code>{user.balance}</code>$\n\n<b>💙 Подписка (часов)</b>: <code>{subhours}</code>\n<b>❤️ PRO Подписка (часов)</b>: <code>{prosubhours}</code>"
    return msg


def profilekb(admin_status: bool):
    keyboard = InlineKeyboardBuilder()
    if admin_status:
        keyboard.row(InlineKeyboardButton(text="⚙️ Админ-Панель", callback_data="adminpanel"))
    keyboard.row(InlineKeyboardButton(text="🛍 Пополнить баланс", callback_data='buyrub'))
    keyboard.row(InlineKeyboardButton(text="🎫 Купить подписку", callback_data="buysub"))

    return keyboard.as_markup(resize_keyboard=True)


@dp.message(F.text == "👨‍💻 Профиль")
async def handleradm(message: types.Message, user: User):
    await bot.send_message(message.from_user.id, profilemsg(message.from_user.full_name, user), reply_markup=profilekb(
        user.tgid in config.admins_ids))


