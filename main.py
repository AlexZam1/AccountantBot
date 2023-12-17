from aiogram.utils import executor
from dispatcher import dp
import handlers
from db import BotDB

BotDB = BotDB('expense_table.db')

if __name__ == '__main__':
    executor.start_polling(dp)
