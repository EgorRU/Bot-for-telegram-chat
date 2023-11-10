from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import BaseFilter
import sqlite3
from asyncio import sleep
from config import ADMIN_API


router = Router()

class FilterLink(BaseFilter):
    async def __call__(self, message: Message):
        return "http" in message.text


async def connection():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(document_id PRIMARY KEY, name TEXT, type TEXT, chat_id TEXT, text TEXT)")
    base.commit()
    return base, cur


async def update_document(document_id, name, chat_id):
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data WHERE name=? and chat_id=?",(name, chat_id)).fetchone()
    if data == None:
        cur.execute("INSERT INTO data(document_id, name, type, chat_id) values(?,?,?,?)",(document_id, name, "document", chat_id))
    else:
        cur.execute("UPDATE data set document_id=? where name=? and chat_id=?", (document_id, name, chat_id))
    base.commit()
    base.close()


async def update_photo(document_id, chat_id):
    base, cur = await connection()
    cur.execute("INSERT INTO data(document_id, type, chat_id) values(?,?,?)",(document_id, "photo", chat_id))
    base.commit()
    base.close()


async def update_link(text, chat_id):
    base, cur = await connection()
    cur.execute("INSERT INTO data(type, chat_id, text) values(?,?,?)",("link", chat_id, text))
    base.commit()
    base.close()
    

@router.message(F.text.startswith("/start"))
async def start(message: Message):
    await message.answer("Ну разраб - дебил, не может сделать генерацию текста здесь. И ваще иди на***")


@router.message(F.text.startswith("/select"))
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
        

@router.message(F.text.startswith("/document"))
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
    

@router.message(F.text.startswith("/photo"))
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
  

@router.message(F.text.startswith("/link"))
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
    

@router.message(F.text.startswith('/alldocument'))
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


@router.message(F.text.startswith('/allphoto'))
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
        

@router.message(F.text.startswith('/alllink'))
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
        

@router.message(F.document)
async def get_document(message: Message):
    await update_document(message.document.file_id, message.document.file_name, message.chat.id)
    

@router.message(F.photo)
async def get_photo(message: Message):
    await update_photo(message.photo[-1].file_id, message.chat.id)
    

@router.message(FilterLink())
async def other(message: Message):
    await update_link(message.text, message.chat.id)