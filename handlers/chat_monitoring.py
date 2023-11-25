from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import BaseFilter
from asyncio import sleep
from config import ADMIN_API
from db import connection, update_document, update_photo, update_link


chat_monitoring = Router()


class FilterLink(BaseFilter):
    '''Фильтрация ссылок
    
       Возвращает True, если в сообщение встречено 'http'
    '''
    async def __call__(self, message: Message):
        return "http" in message.text
    

@chat_monitoring.message(F.text.startswith("/start"))
async def start(message: Message):
    await message.answer("Привет, бот сохраняем файлы, фото, ссылки в текущем чате. Для вывод сохраненных данных используйте команды\n/document\n/photo\n/link\n\n/schedule - вывести расписание любой группы ВятГУ")


@chat_monitoring.message(F.text.startswith("/select"))
async def select(message: Message):
    text = message.text.split()
    if len(text)==1:
        await message.answer("И что тебе выводить? Хоть напиши текст какой-то после команды")
    else:
        pattern = text[1].lower()
        base, cur = await connection()
        data = cur.execute(f"SELECT document_id, name FROM data where type=? and chat_id=?", ("document", message.chat.id)).fetchall()
        for val in data:
            document_id = val[0]
            name = val[1].lower()
            if pattern in name:
                await message.answer_document(document=f"{document_id}")
                await sleep(0.2)
        base.close()
        

@chat_monitoring.message(F.text.startswith("/document"))
async def alldocument(message: Message):
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data where type=? and chat_id=?", ("document", message.chat.id)).fetchall()
    data = data[::-1]
    count = 0 
    for val in data:
        document_id = val[0]
        await message.answer_document(document=f"{document_id}")
        await sleep(0.2)
        count += 1
        if count >50:
            break
    base.close()
    

@chat_monitoring.message(F.text.startswith("/photo"))
async def allphoto(message: Message):
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data where type=? and chat_id=?", ("photo", message.chat.id)).fetchall()
    data = data[::-1]
    count = 0
    for val in data:
        document_id = val[0]
        await message.answer_photo(photo=f"{document_id}")
        await sleep(0.2)
        count += 1
        if count >50:
            break
    base.close()
  

@chat_monitoring.message(F.text.startswith("/link"))
async def alllink(message: Message):
    base, cur = await connection()
    data = cur.execute(f"SELECT text FROM data where type=? and chat_id=?", ("link", message.chat.id)).fetchall()
    data = data[::-1]
    count = 0
    for val in data:
        text = val[0]
        await message.answer(text)
        await sleep(0.2)
        count += 1
        if count >50:
            break
    base.close()
    

@chat_monitoring.message(F.text.startswith('/alldocument'))
async def document(message: Message):
    if message.from_user.id == ADMIN_API:
        base, cur = await connection()
        data = cur.execute(f"SELECT document_id FROM data where type=?", ("document",)).fetchall()
        data = data[::-1]
        for val in data:
            document_id = val[0]
            await message.answer_document(document=f"{document_id}")
            await sleep(0.2)
        base.close()
    else:
        await message.answer("Недостаточно прав")


@chat_monitoring.message(F.text.startswith('/allphoto'))
async def photo(message: Message):
    if message.from_user.id == ADMIN_API:
        base, cur = await connection()
        data = cur.execute(f"SELECT document_id FROM data where type=?", ("photo",)).fetchall()
        data = data[::-1]
        for val in data:
            document_id = val[0]
            await message.answer_photo(photo=f"{document_id}")
            await sleep(0.2)
        base.close()
    else:
        await message.answer("Недостаточно прав")
        

@chat_monitoring.message(F.text.startswith('/alllink'))
async def link(message: Message):
    if message.from_user.id == ADMIN_API:
        base, cur = await connection()
        data = cur.execute(f"SELECT text FROM data where type=?", ("link",)).fetchall()
        data = data[::-1]
        for val in data:
            text = val[0]
            await message.answer(text)
            await sleep(0.2)
        base.close()
    else:
        await message.answer("Недостаточно прав")
        

@chat_monitoring.message(F.document)
async def get_document(message: Message):
    await update_document(message.document.file_id, message.document.file_name, message.chat.id)
    

@chat_monitoring.message(F.photo)
async def get_photo(message: Message):
    await update_photo(message.photo[-1].file_id, message.chat.id)
    

@chat_monitoring.message(FilterLink())
async def other(message: Message):
    await update_link(message.text, message.chat.id)