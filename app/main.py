import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from app.routers.bot_router import router
from app.core.config import settings
from app.models.db_helper import db_helper
from app.middlewares.db import DataBaseSession



dp = Dispatcher()


async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp.update.middleware(DataBaseSession(session_pool=db_helper.session_factory))
    dp.include_router(router=router)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print(str(e))


