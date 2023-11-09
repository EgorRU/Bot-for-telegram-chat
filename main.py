from aiogram import Bot, Dispatcher
import asyncio
from update import router
from config import TOKEN_BOT


bot = Bot(token=TOKEN_BOT)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())