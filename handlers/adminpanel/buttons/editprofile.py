from aiogram import types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import dbworker
from dispatcher import dp
from handlers.adminpanel.adminpanel import back_to_admin_keyboard
from handlers.filters import IsAdmin
from handlers.user.profile import profilemsg
from models.models import User


class EditProfileBack(CallbackData, prefix="prback"):
    tgid: int


class EditProfile(StatesGroup):
    waiting_for_id = State()


class EditBalanceState(StatesGroup):
    waiting_for_balance = State()


class EditBalance(CallbackData, prefix="edbp"):
    tgid: int


class UserBan(CallbackData, prefix="usban"):
    tgid: int


class UserOpenProfile(CallbackData, prefix="usop"):
    tgid: int


def edit_profile_keyboard(user: User):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="💸 Редактировать баланс", callback_data=EditBalance(tgid=user.tgid).pack()))
    if user.banstatus:
        kb.row(InlineKeyboardButton(text="🥺 Разбанить пользователя", callback_data=UserBan(tgid=user.tgid).pack()))
    else:
        kb.row(InlineKeyboardButton(text="🔨 Забанить пользователя", callback_data=UserBan(tgid=user.tgid).pack()))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="backtoadmin"))
    return kb.as_markup()


def back_to_profile(tgid: int):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data=EditProfileBack(tgid=tgid).pack()))
    return kb.as_markup()


@dp.callback_query(IsAdmin(), EditProfileBack.filter())
async def editprofile(callback_query: types.CallbackQuery, state: FSMContext, callback_data: EditProfileBack):
    await state.clear()
    user = await dbworker.get_user(callback_data.tgid)
    await callback_query.message.edit_text(profilemsg("вид от лица пользователя", user), reply_markup=edit_profile_keyboard(user))


@dp.callback_query(IsAdmin(), F.data == "editprofile")
async def editprofile(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("<b>Введите ID пользователя</b>", reply_markup=back_to_admin_keyboard())
    await state.set_state(EditProfile.waiting_for_id)


@dp.message(IsAdmin(), EditProfile.waiting_for_id)
async def editprofile(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user = await dbworker.get_user(int(message.text))
        if user:
            await state.clear()
            await message.answer(profilemsg("вид от лица пользователя", user), reply_markup=edit_profile_keyboard(user))
        else:
            await message.answer("<b>Пользователь не найден!</b>")
    else:
        await message.answer("<b>Это не число!</b>")


@dp.callback_query(IsAdmin(), UserBan.filter())
async def banuser(callback_query: types.CallbackQuery, callback_data: UserBan):
    user = await dbworker.get_user(callback_data.tgid)
    if user.banstatus:
        user.banstatus = False
        await user.save()
        await callback_query.answer(show_alert=True, text="Пользователь успешно разбанен!")
        await callback_query.message.edit_text(profilemsg("вид от лица пользователя", user), reply_markup=edit_profile_keyboard(user))
    else:
        user.banstatus = True
        await user.save()
        await callback_query.answer(show_alert=True, text="Пользователь успешно забанен!")
        await callback_query.message.edit_text(profilemsg("вид от лица пользователя", user), reply_markup=edit_profile_keyboard(user))


@dp.callback_query(IsAdmin(), EditBalance.filter())
async def edit_balance(callback_query: types.CallbackQuery, callback_data: EditBalance, state: FSMContext):
    await callback_query.message.edit_text("<b>Введите новый баланс пользователя</b>", reply_markup=back_to_profile(tgid=callback_data.tgid))
    await state.set_state(EditBalanceState.waiting_for_balance)
    await state.update_data({"user_id": callback_data.tgid})


@dp.message(IsAdmin(), EditBalanceState.waiting_for_balance)
async def edit_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        await state.clear()

        user = await dbworker.get_user(data["user_id"])
        user.balance = int(message.text)
        await user.save()
        await message.answer("<b>Успешно!</b>", reply_markup=back_to_profile(user.tgid))
    else:
        await message.answer("<b>Это не число!</b>")