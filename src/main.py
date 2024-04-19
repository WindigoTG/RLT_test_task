import asyncio

from config.config import load_config
from database.database import Database
from aiogram import Bot, Dispatcher

from handlers.standard_handlers import router


async def main():
    """"""
    config = load_config()

    print('Connecting to DB')

    if not await Database.connect_to_database(config.database.connection_uri):
        print('Unable to connect to database')
        return

    db_collection = Database.get_collection(
        config.database.db_name,
        config.database.collection_name,
    )

    dp = Dispatcher(db_collection=db_collection)
    bot = Bot(token=config.telegram_bot.token)

    dp.include_router(router)

    print('Launching bot')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
