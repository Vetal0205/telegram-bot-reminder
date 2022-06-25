import os
import logging
import Reminder
import Exceptions
from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_calendar import SimpleDateTime, calendar_callback, time_callback

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    Task = State()
    Date = State()
    Time = State()
    Insert = State()

@dp.message_handler(commands=['cancel'], state='*')
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.reply('There are no actions to cancel.')
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Cancelled', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['help'])
async def cmd_start(message: Message):
    await message.reply(
        """Welcome to the telegram-bot-reminder! Here you can here you can leave reminders for your cases,
        all you need is to write the task itself, and when you are reminded of it, everything is simple! To start 
        click on /start or /new ! ) """)


@dp.message_handler(commands=['start', 'new'])
async def start_handler(message: Message):
    await Form.Task.set()
    await message.answer("Please write a task!")


@dp.message_handler(state=Form.Task)
async def task_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['Task'] = message.text
    await Form.next()
    await message.answer("Please select a date: ", reply_markup=await SimpleDateTime().start_calendar())


# simple calendar usage
@dp.callback_query_handler(calendar_callback.filter(), state=Form.Date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleDateTime().process_selection_calendar(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['Date'] = date.strftime("%d/%m/%Y")
        await Form.next()
        await callback_query.message.edit_text(
            f'You selected {date.strftime("%d/%m/%Y")}\nPlease select a time:',
            reply_markup=await SimpleDateTime().start_hour()
        )


@dp.callback_query_handler(time_callback.filter(), state=Form.Time)
async def process_simple_time(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, time = await SimpleDateTime().process_selection_time(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            data['Time'] = time
            await callback_query.message.edit_text(
                f"""Please check your inputs:\n\nTask: {data['Task']}\nDate: {data["Date"]}\nTime: {data['Time']}.\n
                \nIf it is incorrect type /cancel and input again, otherwise /accept""")
            await Form.next()


@dp.message_handler(commands=['accept'], state=Form.Insert)
async def insertion_data_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            task = Reminder.add_task(data['Date'], data['Time'], data['Task'])
        except Exception as e:
            await state.finish()
            await message.answer(str(e))
            return
    answer_msg = (f"Added task:\n{task.task}\n"
                  f"The date is set for {task.date}\n"
                  f"The time is set for {task.time}")
    await message.answer(answer_msg)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
