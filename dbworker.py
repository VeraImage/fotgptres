
from peewee_aio import Manager

from models.models import User, Purchase, Build

manager = Manager('aiosqlite:///db.sqlite')


async def add_user(tgid: int):
    return await User.create(tgid=tgid)


async def get_user(tgid):
    if isinstance(tgid, int) or tgid.isdigit():
        user = await User.select().where(User.tgid == int(tgid)).first()
    else:
        user = await User.select().where(User.username == tgid).first()

    return user


async def get_all_users():
    return await User.select()


async def add_purchase(type: str, sum: int, user_id: int, date):
    return await Purchase.create(type=type, sum=sum, user_id=user_id, date=date)


async def get_all_purchases():
    return await Purchase.select()

async def add_build(user_id: int, build_id: str):
    return await Build.create(tgid=user_id, build_id=build_id)


async def get_builds_by_user_id(user_id: int):
    return await Build.select().where(Build.tgid == user_id)


async def get_build_by_build_id(build_id: str):
    return await Build.select().where(Build.build_id == build_id).first()