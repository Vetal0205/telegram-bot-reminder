import datetime
import os
import logging
import Reminder
import Exceptions
from midlewares import AccessMiddleware
from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_calendar import SimpleDateTime, callback

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ACCESS_ID = os.getenv("TELEGRAM_ACCESS_ID")
# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m.%d.%Y %a %H:%M:%S', level=logging.INFO)
# Initialize bot and dispatcher

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))

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
    logging.info('From %s: %s', message.from_user.id, message.text)
    await message.reply(
        """Welcome to the telegram-bot-reminder! Here you can here you can leave reminders for your cases,
        all you need is to write the task itself, and when you are reminded of it, everything is simple! To start 
        click on /start or /new ! ) """)


@dp.message_handler(commands=['start', 'new'])
async def start_handler(message: Message):
    logging.info('From %s: %s', message.from_user.id,  message.text)
    await Form.Task.set()
    await message.answer("Please write a task!")


@dp.message_handler(state=Form.Task)
async def task_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['Task'] = message.text
        logging.info('From %s: State \"Task\" update: %s',  message.from_user.id, message.text)
    await Form.next()
    await message.answer("Please select a date: ", reply_markup=await SimpleDateTime().start_calendar())


# simple calendar usage
@dp.callback_query_handler(callback.filter(), state=Form.Date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        selected, date = await SimpleDateTime().process_selection_calendar(callback_query, callback_data)
        if selected:
            async with state.proxy() as data:
                year, month, day = date
                date = datetime.date(year,month,day)
                data['Date'] = date.strftime("%d/%m/%Y")
                logging.info('From %s: State \"Date\" update: %s', callback_query.from_user.id, data['Date'])
            await Form.next()
            await callback_query.message.edit_text(
                f'You selected {date.strftime("%d/%m/%Y")}\nPlease select a time:',
                reply_markup=await SimpleDateTime().start_hour(year, month, day)
            )
    except Exceptions.IncorrectDateTime as e:
        await callback_query.message.answer(str(e), reply_markup=await SimpleDateTime().start_calendar())
        logging.error('Exception from %s: %s ', callback_query.from_user.id, str(e))



@dp.callback_query_handler(callback.filter(), state=Form.Time)
async def process_simple_time(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    try:
        selected, time = await SimpleDateTime().process_selection_time(callback_query, callback_data)
        if selected:
            async with state.proxy() as data:
                data['Time'] = time
                logging.info('From %s: State \"Time\" update: %s', callback_query.from_user.id, data['Time'])
                await callback_query.message.edit_text(
                    f"""Please check your inputs:\n\nTask: {data['Task']}\nDate: {data["Date"]}\nTime: {data['Time']}.\n
                    \nIf it is incorrect type /cancel and input again, otherwise /accept""")
                await Form.next()
    except Exceptions.IncorrectDateTime as e:
        await callback_query.message.answer(str(e), reply_markup=await SimpleDateTime().start_hour())
        logging.error('Exception from %s: %s ', callback_query.from_user.id, str(e))


@dp.message_handler(commands=['accept'], state=Form.Insert)
async def insertion_data_handler(message: Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            task = Reminder.add_task(data['Date'], data['Time'], data['Task'])
        except Exception as e:
            await state.finish()
            logging.error('Exception from %s: %s', message.from_user.id, str(e))
            return
    logging.info('From %s: Added task: %s, %s, %s', message.from_user.id,  data['Date'], data['Time'], data['Task'])
    answer_msg = (f"Added task:\n{task.task}\n"
                  f"The date is set for {task.date}\n"
                  f"The time is set for {task.time}")
    await message.answer(answer_msg)
    await state.finish()


@dp.message_handler(commands=['tasks'])
async def get_all_tasks(message: Message):
    logging.info('From %s: %s', message.from_user.id,  message.text)
    recent_tasks = Reminder.get_all_tasks()
    if not recent_tasks:
        await message.answer("You don`t have any tasks now")
        return
    recent_tasks_rows = [f"Task: {task.task} on {task.date} {task.time}\nPress /del{task.id} to delete" for task in
                         recent_tasks]
    answer_message = "\n\n".join(recent_tasks_rows)
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_task(message: Message):
    row_id = message.text
    try:
        Reminder.del_task(row_id)
    except Exceptions.NotCorrectMessage as e:
        logging.error('Exception from %s: %s', message.from_user.id, str(e))
        await message.answer(str(e))
    logging.info('From %s: Task %s deleted', message.from_user.id, row_id)
    await message.answer("Deleted")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
