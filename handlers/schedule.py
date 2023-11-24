from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters import BaseFilter
from bs4 import BeautifulSoup
from typing import Union
from asyncio import sleep
import requests
import aspose.pdf as ap
from db import connection


schedule = Router()
list_groups = []


class ScheduleGroups(StatesGroup):
    name_group = State()
 

class FilterGroup(BaseFilter):
    '''Фильтрация callback
    
       Возвращает True, если нажата кнопка с раписанием
    '''
    async def __call__(self, callback: Message):
        list_groups = await get_name_group()
        return callback.data in list_groups


async def get_name_group() ->list[str]:
    '''Получение списка группа с сайта вуза
    '''
    try:
        response = requests.get("https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html")
        soup = BeautifulSoup(response.text, 'lxml')
        list_groups = soup.find_all('div', class_='grpPeriod')
        list_groups = [value.text.strip() for value in list_groups]
    except:
        return
    return list_groups


async def BuildKeyboardButton(list_input_group) -> list[InlineKeyboardButton]:
    '''Получение клавиатуры со списком групп
    '''
    ListKeyboardButton = []
    for group in list_groups:
        for input_group in list_input_group:
            if input_group.lower() in group.lower():
                ListKeyboardButton.append([InlineKeyboardButton(text=f'{group}', callback_data=f'{group}')])
    return ListKeyboardButton


async def get_schedule(name_group) -> Union[str, None]:
    '''Получение ссылки на расписание
    '''
    try:
        response = requests.get("https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html")
        html = response.text
        index = html.find(name_group)
        html = html[index:]
        index = html.find("href")
        html = html[index+6:]
        index = 0
        url = "https://www.vyatsu.ru"
        while html[index]!="\"":
            url += html[index]
            index += 1
    except:
        return
    # response = requests.get(url)
    # reverse_url = url[::-1]
    # name_file = ""
    # index = 0
    # while reverse_url[index]!='/':
    #     name_file += reverse_url[index]
    #     index += 1
    # name_file = name_file[::-1]
    # with open(name_file, 'wb') as file: 
    #     file.write(response.content)
    return url


@schedule.message(StateFilter(None), Command("schedule"))
async def FSMschedule(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data='Отмена')]])
    await message.answer("Напишите учебную групу в виде: Подб-3 или ФиКм-2", reply_markup=keyboard)
    await state.set_state(ScheduleGroups.name_group)


@schedule.callback_query(ScheduleGroups.name_group, F.data == 'Отмена')
async def cancel_state(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.answer()
    

@schedule.message(ScheduleGroups.name_group)
async def find_name_group(message: Message, state: FSMContext):
    #если написали команду, то отменяем машину состояний и выполняем действие по команде
    list_command = ['/start', '/select', '/document', '/photo', '/link',
                    '/start@DataFullBot', '/select@DataFullBot', '/document@DataFullBot', '/photo@DataFullBot', '/link@DataFullBot']
    if message.text in list_command or message.text[:7] == '/select':
        await state.clear()
        base, cur = await connection()
        if message.text[:6] == '/start':
            await message.answer("Привет, бот сохраняем файлы, фото, ссылки в текущем чате. Для вывод сохраненных данных используйте команды\n/document\n/photo\n/link\n\n/schedule - вывести расписание любой группы ВятГУ")
        elif message.text[:7] == '/select':
            text = message.text.split()
            if len(text)==1:
                await message.answer("И что тебе выводить? Хоть напиши текст какой-то после команды")
            else:
                pattern = text[1].lower()
                data = cur.execute(f"SELECT document_id, name FROM data where type=? and chat_id=?", ("document", message.chat.id)).fetchall()
                for val in data:
                    document_id = val[0]
                    name = val[1].lower()
                    if pattern in name:
                        await message.answer_document(document=f"{document_id}")
                        await sleep(0.2)
        elif message.text[:9] == '/document':
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
        elif message.text[:6] == '/photo':
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
        elif message.text[:5] == '/link':
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
    #иначе ищем расписание у группы
    else:
        global list_groups
        if len(list_groups)==0:
            list_groups = await get_name_group()
        if list_groups == None:
            await message.answer("Сервер не доступен")
            await state.clear()
        else:
            input_group = [message.text]
            input_split = input_group[0].split("-")
            list_symbol = ['б', 'м', 'а', 'с']
            if len(input_split)==2 and input_split[0][-1] not in list_symbol:
                for i in list_symbol:
                    input_group.append(f"{input_split[0]}{i}-{input_split[1]}")
            ListKeyboardButton = await BuildKeyboardButton(input_group)
            if len(ListKeyboardButton)==0:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Отмена', callback_data='Отмена')]])
                await message.answer("Не могу найти такую группу, попробуйте ещё раз ввести группу", reply_markup=keyboard)
            elif len(ListKeyboardButton)==1:
                name_group = ListKeyboardButton[0][0].text
                url = await get_schedule(name_group)
                if url!=None:
                    await message.answer(url)
                else:
                    await message.answer("Сервер не доступен")
                await state.clear()
            else:
                keyboard = InlineKeyboardMarkup(inline_keyboard=ListKeyboardButton)
                await message.answer("Выберите группу", reply_markup=keyboard)
                await state.clear()
            

@schedule.callback_query(FilterGroup())
async def get_schedule_for_group(callback):
    name_group = callback.data
    url = await get_schedule(name_group)
    if url != None:
        await callback.message.answer(url)
    else:
        await callback.message.answer("Сервер не доступен")
    await callback.answer()
    