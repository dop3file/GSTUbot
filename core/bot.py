from aiogram import Bot, Dispatcher
from aiogram import types
from aiogram.utils import executor
from aiogram.types import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
from query import QueryNameException, Query, QueryUtils


class _Bot:
    def __init__(self, query_factory):
        self.query_factory = query_factory
        self.bot = Bot(config.BOT_TOKEN, parse_mode=ParseMode.HTML)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

        self.dp.register_message_handler(self.query_router, commands=['query'])
        executor.start_polling(dispatcher=self.dp, skip_updates=True)

    async def query_router(self, message: types.Message):
        commands = {
            'get': self.get_members,
            'add': self.add_member,
            'create': self.create_query,
        }

        arguments = message.get_args().split(' ')

        if len(arguments) >= 2:
            command = arguments[0]
            query_name = arguments[1]

            try:
                await commands.get(command)(message, query_name)
            except QueryNameException:
                await message.answer("Ошибка имени, возможно такой очереди не существует")

    async def get_members(self, message: types.Message, query_name: str) -> None:
        query: Query = self.query_factory.get_query(query_name)
        query_members: str = QueryUtils.get_stylish_members(query.get_all_members())
        await message.answer(f'Очередь "{query_name}"\n\n{query_members}')
    
    async def add_member(self, message: types.Message, query_name: str) -> None:
        query = self.query_factory.get_query(query_name)
        query.add_member(query_position=-1, telegram_username=message.from_user.username)
        await message.answer(f'Вы добавлены в очередь "{query_name}"')  

    async def create_query(self, message: types.Message, query_name: str) -> None:
        self.query_factory.add_query(query_name)
        await message.answer(f'Очередь "{query_name}" создана')

