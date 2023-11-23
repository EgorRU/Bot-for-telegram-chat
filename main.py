from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from handlers.chat_monitoring import chat_monitoring
from handlers.schedule import schedule
from config import TOKEN_BOT


bot = Bot(token=TOKEN_BOT)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    dp.include_router(chat_monitoring)
    dp.include_router(schedule)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())