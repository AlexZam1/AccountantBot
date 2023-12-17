from aiogram import Bot, Dispatcher
from config import tg_bot_token
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=tg_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)