import sqlite3


async def connection():
    '''Подключение в базе данных SQlite
    '''
    base = sqlite3.connect("database.db")
    cur = base.cursor()
    base.execute("CREATE TABLE IF NOT EXISTS data(document_id PRIMARY KEY, name TEXT, type TEXT, chat_id TEXT, text TEXT)")
    base.commit()
    return base, cur


async def update_document(document_id, name, chat_id) -> None:
    '''Запоминает id документа, id чата, название документа
    
       Все данные сохраняются в бд
    '''
    base, cur = await connection()
    data = cur.execute(f"SELECT document_id FROM data WHERE name=? and chat_id=?",(name, chat_id)).fetchone()
    if data == None:
        cur.execute("INSERT INTO data(document_id, name, type, chat_id) values(?,?,?,?)",(document_id, name, "document", chat_id))
    else:
        cur.execute("UPDATE data set document_id=? where name=? and chat_id=?", (document_id, name, chat_id))
    base.commit()
    base.close()


async def update_photo(document_id, chat_id) -> None:
    '''Запоминает id фото, id чата
    
       Все данные сохраняются в бд
    '''
    base, cur = await connection()
    cur.execute("INSERT INTO data(document_id, type, chat_id) values(?,?,?)",(document_id, "photo", chat_id))
    base.commit()
    base.close()


async def update_link(text, chat_id) -> None:
    '''Запоминает сообщение со ссылкой
    
       Все данные сохраняются в бд
    '''
    base, cur = await connection()
    cur.execute("INSERT INTO data(type, chat_id, text) values(?,?,?)",("link", chat_id, text))
    base.commit()
    base.close()