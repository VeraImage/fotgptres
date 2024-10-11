from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import dbworker
from dispatcher import bot, dp
from handlers.adminpanel.adminpanel import back_to_admin_keyboard
from handlers.filters import IsAdmin
from handlers.user.start import getstartkeyboard


class MailingMsg(StatesGroup):
    waiting_for_message = State()


def delmekb():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Скрыть сообщение.", callback_data="delme"))


@dp.callback_query(F.data == "delme")
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.answer()
    await callback_query.message.delete()


@dp.callback_query(F.data == "mailing")
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "<b>Введите сообщение, также вы можете прикрепить фото или видео(не документ!)\n</b>",
        reply_markup=back_to_admin_keyboard(),
    )
    await state.set_state(MailingMsg.waiting_for_message)


@dp.message(IsAdmin(), F.text | F.photo | F.animation | F.video, MailingMsg.waiting_for_message)
async def start(message: types.Message, state: FSMContext):
    count = 0
    countnotsuccess = 0
    await state.clear()
    msg = await bot.send_message(
        message.from_user.id,
        "<b>Начинаю рассылку...</b>",
        reply_markup=getstartkeyboard(),
    )
    for user in await dbworker.get_all_users():
        try:
            if message.photo:
                await bot.send_photo(
                    user.tgid,
                    message.photo[0].file_id,
                    caption=message.html_text,
                    reply_markup=delmekb(),
                )
            elif message.animation:
                await bot.send_animation(
                    user.tgid,
                    message.animation.file_id,
                    caption=message.html_text,
                    reply_markup=delmekb(),
                )
            elif message.video:
                await bot.send_video(
                    user.tgid,
                    message.video.file_id,
                    caption=message.html_text,
                    reply_markup=delmekb(),
                )
            else:
                await bot.send_message(
                    user.tgid,
                    message.html_text,
                    reply_markup=delmekb(),
                )
            count += 1
        except:
            countnotsuccess += 1
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    await bot.send_message(
        message.from_user.id,
        f"<b>Успешно отправлено:</b> <code>{count}</code>\n<b>Не успешно(заблокировали бота):</b> <code>{countnotsuccess}</code>",
        reply_markup=getstartkeyboard(),
    )
