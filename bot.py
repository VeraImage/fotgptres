from dispatcher import dp, bot
import asyncio
from loguru import logger
import inspect
import handlers
import models.models


async def main():
    documents = [
        a[1]
        for a in inspect.getmembers(
            models.models,
            lambda member: inspect.isclass(member) and member.__module__ == "models.models",
        )
    ]

    for i in documents:
        await i.create_table()

    sessions = [dp.start_polling(bot)]
    await asyncio.gather(*sessions)


if __name__ == "__main__":
    logger.add(
        "logs/latest.log",
        level="INFO",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="30 KB",
        compression="zip",
    )
    logger.info("Started!")

    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
