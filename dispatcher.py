import logging
from aiogram.fsm.storage.memory import MemoryStorage
from config import token
from aiogram import Bot, Dispatcher

from middlewares.db_middleware import DBMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
dp.update.outer_middleware(DBMiddleware())
