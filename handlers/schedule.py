from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup
import requests


schedule = Router()
list_groups = []


class ScheduleGroups(StatesGroup):
    name_group = State()
    

async def get_name_group():
    try:
        response = requests.get("https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html")
        soup = BeautifulSoup(response.text, 'lxml')
        list_groups = soup.find_all('div', class_='grpPeriod')
        list_groups = [value.text.strip() for value in list_groups]
    except:
        return
    return list_groups


async def BuildKeyboardButton(input_group):
    ListKeyboardButton = []
    for group in list_groups:
        if input_group.lower() in group.lower():
            ListKeyboardButton.append([InlineKeyboardButton(text=f'{group}', callback_data=f'{group}')])
    return ListKeyboardButton


async def get_schedule(name_group):
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
    await callback.message.answer("Отменено")
    await callback.answer()
    

@schedule.message(ScheduleGroups.name_group)
async def find_name_group(message: Message, state: FSMContext):
    global list_groups
    
    if len(list_groups)==0:
        list_groups = await get_name_group()
        
    if list_groups == None:
        await message.answer("Сервер не доступен")
        await state.clear()
    else:
        input_group = message.text
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
            

@schedule.callback_query(F.data)
async def get_schedule_for_group(callback):
    name_group = callback.data
    url = await get_schedule(name_group)
    if url != None:
        await callback.message.answer(url)
    else:
        await callback.message.answer("Сервер не доступен")
    await callback.answer()
    