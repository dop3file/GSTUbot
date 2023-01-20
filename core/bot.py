from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup, KeyboardButton, \
                          InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

import config

from query import QueryNameException
from main import query_factory


class _Bot:
    bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())

    @dp.message_handler(commands=['query'], state='*')
    async def query_router(message: types.Message):
        commands = {
            'get': _Bot.get_members,
            'add': _Bot.add_member,
            'create': _Bot.create_query,
        }

        if list(message.text).count(' ') >= 2:
            command = message.text.split(' ')[1]
            query_name = message.text.split(' ')[2]
            try:
                await commands.get(command)(message, query_name)
            except QueryNameException:
                await message.answer("Ошибка имени, возможно такой очереди не существует")

    async def get_members(message, query_name):
        query_members: list = query_factory.get_query(query_name).get_all_members()
        query_members_str = '\n'.join([f"{int(count)}. @{member}" for member, count in query_members])
        await message.answer(f'Очередь "{query_name}"\n\n{query_members_str}')

    async def add_member(message, query_name):
        query = query_factory.get_query(query_name)
        query.add_member(query.get_count_members() + 1, message.from_user.username)
        await message.answer(f'Вы добавлены в очередь "{query_name}"')  

    async def create_query(message, query_name):
        query = query_factory.add_query(query_name)
        await message.answer(f'Очередь "{query_name}" создана')



bot = _Bot()

executor.start_polling(dispatcher=bot.dp, skip_updates=True)