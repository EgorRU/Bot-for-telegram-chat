from aiogram import Router, F
from aiogram.types import Message
import sqlite3

router = Router()


async def connection():
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(id_document PRIMARY KEY, name TEXT, type TEXT)")
    base.commit()
    return base, cur


async def update_document(id_document, name):
    base, cur = await connection()
    data = cur.execute(f"SELECT id_document FROM data WHERE name=?",(name,)).fetchone()
    if data == None:
        cur.execute("INSERT INTO data values(?,?,?)",(id_document, name, "document"))
    else:
        cur.execute("UPDATE data set id_document=? where name==?", (id_document, name))
    base.commit()
    base.close()


async def update_photo(id_document):
    base, cur = await connection()
    cur.execute("INSERT INTO data(id_document, type) values(?,?)",(id_document, "photo"))
    base.commit()
    base.close()


@router.message(F.text == '/start')
async def start(message: Message):
    await message.answer("Не пиши мне такое, забаню")


@router.message(F.text == '/allshow')
async def allshow(message: Message):
    base, cur = await connection()
    data = cur.execute(f"SELECT id_document FROM data where type=?", ("document",)).fetchall()
    for val in data:
        id_document = val[0]
        await message.answer_document(document=f"{id_document}")
    base.close()
    

@router.message(F.text.startswith("/select"))
async def select(message: Message):
    text = message.text.split()
    if len(text)==1:
        await message.answer("И что тебе выводить? Хоть напиши текст какой-то после команды")
    else:
        pattern = text[1].lower()
        base, cur = await connection()
        data = cur.execute(f"SELECT id_document, name FROM data where type=?", ("document",)).fetchall()
        for val in data:
            id_document = val[0]
            name = val[1].lower()
            if pattern in name:
                await message.answer_document(document=f"{id_document}")
        base.close()
        

@router.message(F.text == '/play')
async def play(message: Message):
    await message.answer("Тут типо что-то тоже делаю, машину состояний, или ещё какую дичь")
    

@router.message(F.text == '/message')
async def message(message: Message):
    await message.answer("Типо здесь генерирую текст нейросетью")
    

@router.message(F.document)
async def get_document(message: Message):
    await update_document(message.document.file_id, message.document.file_name)


@router.message(F.photo)
async def get_photo(message: Message):
    await update_photo(message.photo[-1].file_id)