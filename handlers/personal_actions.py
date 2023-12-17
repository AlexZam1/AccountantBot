from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from main import BotDB
from dispatcher import dp


categories = {
    "еда": {'food', 'breakfast', 'dinner', 'lunch', 'products', 'еда', 'завтрак', 'обед', 'ужин', 'продукты'},
    "транспорт": {'transport', 'metro', 'ticket', 'plane', 'train', 'bus', 'taxi', 'транспорт', 'метро', 'билет',
                  'автобус', 'самолет', 'поезд', 'электричка', 'автобус', 'такси', 'самокат', 'прокат',
                  'каршеринг'},
    "связь": {'link', 'phone', 'internet', 'sim', 'связь', 'телефон', 'интернет', 'сим'},
    "магазины": {'market', 'shop', 'clothes', 'маркет', 'магазин', 'одежда', 'рынок'},
    "прочее": {}
}


class Form(StatesGroup):
    """создаем класс состояния бота, между которыми будем переключаться для считывания трат"""
    name = State()
    amount = State()


exceptions = {"Внести расход", "/spent", "История", "/history", "Статистика", "/stat"}


@dp.message_handler(commands=["start"])
@dp.message_handler(Text(equals='Старт'))
@dp.message_handler(lambda message: message.text not in exceptions)
async def start_commands(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton(text="Внести расход")
    keyboard.add(button_1)
    button_2 = "История"
    keyboard.add(button_2)
    button_3 = "Статистика"
    keyboard.add(button_3)
    await message.reply(f"Привет, {message.from_user.first_name}!\n\n"
                        "Я бот, который поможет тебе вести учет ежедневных расходов.\n\n"
                        "Нажми на кнопку или напиши:\n\n"
                        "- /spent, если хочешь внести расход;\n\n"
                        "- /history, чтобы узнать историю последних 7 трат;\n\n"
                        "- /stat для просмотра статистики.", reply_markup=keyboard)


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')


@dp.message_handler(commands=["spent"])
@dp.message_handler(Text(equals='Внести расход'))
async def start_commands(message: types.Message):
    await Form.name.set()
    await message.reply("Внеси название расхода или напиши /cancel")


# Сюда приходит ответ с названием затраты
@dp.message_handler(lambda message: (message.text not in exceptions) and (len(message.text) < 31), state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text.lower()

    await Form.next()
    await message.reply("Сколько рублей ты потратил?")


# Напоминаем, что нужно указать количество рублей
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.amount)
async def process_age_invalid(message: types.Message):
    return await message.reply("Напиши количество рублей или напиши /cancel")


# Принимаем количество, потраченных рублей
@dp.message_handler(lambda message: message.text.isdigit() and len(message.text) < 12, state=Form.amount)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['amount'] = int(message.text)

    name = data['name']
    amount = data['amount']
    cur_user_id = message.from_user.id

    category_spending = 'прочее'
    for category in categories:
        if name in categories[category]:
            category_spending = category

    BotDB.insert_db(name, amount, cur_user_id, category_spending)

    await message.answer(f"Затрата по пункту \"{name}\" стоимостью {amount} руб. учтена!")
    await state.finish()


# Показывает последние 7 расходов
@dp.message_handler(commands=["history"])
@dp.message_handler(Text(equals='История'))
async def start_commands(message: types.Message):
    cur_user_id = message.from_user.id
    if BotDB.treats_history:
        last_expense = [
            f"Трата \"{i[1]}\" за {i[2]} руб. была {i[4]}"
            for i in BotDB.treats_history(cur_user_id)]
        last_expenses = "Последние траты:\n\n* " + "\n\n* ".join(last_expense)
        await message.answer(last_expenses)
    else:
        await message.reply('Вы еще не вносили затраты!')


# Показывает сумму трат от времени и категории
@dp.message_handler(commands=["stat"])
@dp.message_handler(Text(equals='Статистика'))
async def start_commands(message: types.Message):
    cur_user_id = message.from_user.id
    stat_expense = [
        f"*{categ} - {BotDB.sum_categ_expenses(cur_user_id, categ)}"
        for categ in categories]
    stat_expense = "Статистика трат по категориям за всё время:\n\n " + "\n\n ".join(stat_expense)

    stat_history_expense = BotDB.sum_history_expenses(cur_user_id)
    for i in range(len(stat_history_expense)):
        if stat_history_expense[i]:
            stat_history_expense[i] = str(stat_history_expense[i]) + " руб."
        else:
            stat_history_expense[i] = "траты отсутствуют"

    await message.answer(f"Статистика трат по времени:\n\n"
                         f"*Сегодня - {stat_history_expense[0]}\n\n"
                         f"*Вчера - {stat_history_expense[1]}\n\n"
                         f"*Неделя - {stat_history_expense[2]}\n\n"
                         f"*Месяц - {stat_history_expense[3]}\n\n"
                         f"*За все время - {stat_history_expense[4]}\n\n"
                         f"{stat_expense}")
