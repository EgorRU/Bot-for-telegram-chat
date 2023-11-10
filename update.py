from aiogram import Router, F
from aiogram.types import Message
import sqlite3
from config import ADMIN_API


router = Router()


async def connection():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(document_id PRIMARY KEY, name TEXT, type TEXT, chat_id TEXT)")
    base.commit()
    return base, cur


async def update_document(document_id, name, chat_id):
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data WHERE name=? and chat_id=?",(name, chat_id)).fetchone()
    if data == None:
        cur.execute("INSERT INTO data values(?,?,?,?)",(document_id, name, "document", chat_id))
    else:
        cur.execute("UPDATE data set document_id=? where name=? and chat_id=?", (document_id, name, chat_id))
    base.commit()
    base.close()


async def update_photo(document_id, chat_id):
    base, cur = await connection()
    cur.execute("INSERT INTO data(document_id, type, chat_id) values(?,?,?)",(document_id, "photo", chat_id))
    base.commit()
    base.close()


@router.message(F.text.startswith("/start"))
async def start(message: Message):
    await message.answer("Не пиши мне такое, забаню")


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
        base.close()
        

@router.message(F.text.startswith("/alldocument"))
async def allshow(message: Message):
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data where type=? and chat_id=?", ("document", message.chat.id)).fetchall()
    for val in data:
        document_id = val[0]
        await message.answer_document(document=f"{document_id}")
    base.close()
    

@router.message(F.text.startswith("/allphoto"))
async def select(message: Message):
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data where type=? and chat_id=?", ("photo", message.chat.id)).fetchall()
    for val in data:
        document_id = val[0]
        await message.answer_photo(photo=f"{document_id}")
    base.close()
  
    
@router.message(F.text == '/all')
async def info(message: Message):
    if message.from_user.id == ADMIN_API:
        base, cur = await connection()
        data = cur.execute(f"SELECT document_id FROM data where type=?", ("document",)).fetchall()
        for val in data:
            document_id = val[0]
            await message.answer_document(document=f"{document_id}")
        base.close()
    else:
        await message.answer("Недостаточно прав")


@router.message(F.document)
async def get_document(message: Message):
    await update_document(message.document.file_id, message.document.file_name, message.chat.id)
    

@router.message(F.photo)
async def get_photo(message: Message):
    await update_photo(message.photo[-1].file_id, message.chat.id)