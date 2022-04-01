import datetime

import telebot
import locale
from src.parser import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import types
from models.user import User
from models.todo import ToDo

import cfg

# TODO учитывать время клиента
# TODO хранение работ scheduler'а в бд с последующей синхронизацией
# TODO добавить кнопку меню при открытии диалогаъ

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

bot = telebot.TeleBot(cfg.API_TOKEN)

schedule = BlockingScheduler()

blocking_state = ['creating todo', 'edit name', 'edit datetime']


# TODO добавить выбор периодичности напоминания

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """\
    Привет! Я NotifyBot.
Я буду помогать тебе не забыть важные события или дела, которые необходимо сделать!\
 Для получения доступного списка команд введи /help
    """)
    current_user = User(user_id=message.from_user.id)
    if current_user.get_user() is None:
        User.insert_user(current_user.user_id, current_user)
    else:
        current_user = current_user.get_user()
    User.db_sync(current_user.user_id)
    ToDo.db_sync(current_user.user_id)

    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("/menu"))
    markup.add(types.KeyboardButton("/help"))
    markup.add(types.KeyboardButton("/start"))
    bot.send_message(message.chat.id, 'Список команд', reply_markup=markup)


@bot.message_handler(commands=['help'])
def get_commands_list(message):
    bot.reply_to(message, """\
    /start - старт бота.
/menu - меню бота
        """)


@bot.message_handler(commands=['menu'])
def set_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Добавить событие", callback_data='create_todo'))
    markup.add(types.InlineKeyboardButton("Показать список событий", callback_data='get_list'))
    bot.send_message(message.chat.id, 'Меню', reply_markup=markup)


def get_todo_list(message: str, user_id: int):
    markup = types.InlineKeyboardMarkup()
    user = User.get(user_id)
    todos = ToDo.get(user[0].user_id)
    if todos:
        for todo in todos:
            datetime_of_todo = datetime.datetime.strptime(todo.date_of_todo, '%Y-%m-%d %H:%M:%S')
            markup.add(types.InlineKeyboardButton(
                f"{todo.name_of_todo} - {datetime_of_todo.strftime(u'%d %B в %H:%M')}",
                callback_data=f"{todo.get_id()}"))
        bot.send_message(message.chat.id, 'Список напоминаний', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Список напоминаний пуст')


def get_todo_from_callback(todo_id: int, user_id: int, todo_list: list):
    selected_todo = None
    for todo in todo_list:
        if todo.get_id() == todo_id and todo.user_id == user_id:
            selected_todo = todo
    return selected_todo


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    user = User.get(call.from_user.id)
    todo_list = ToDo.get(user[0].user_id)
    data = call.data
    splited_data = data.split(' ')
    if splited_data[0] == 'get_list':
        get_todo_list(call.message, call.from_user.id) if bot.get_state(
            call.from_user.id) not in blocking_state else bot.send_message(
            call.message.chat.id,
            'Нельзя просматривать список на этапе создания или редактирования события')
    if splited_data[0] == 'create_todo':
        bot.set_state(call.from_user.id, 'creating todo')
        todo = ToDo(user_id=call.from_user.id)
        todo.create_todo()
        bot.send_message(call.message.chat.id, 'О чем нужно напомнить?', parse_mode='html')
    elif splited_data[0].isdigit() and int(splited_data[0]) in map(lambda x: x.get_id(), todo_list):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Изменить название", callback_data=f'edit_name {splited_data[0]}'))
        markup.add(
            types.InlineKeyboardButton("Изменить дату и время", callback_data=f'edit_datetime {splited_data[0]}'))
        markup.add(types.InlineKeyboardButton("Удалить", callback_data=f'delete {splited_data[0]}'))
        bot.send_message(call.message.chat.id, 'Что нужно сделать с напоминанием?', reply_markup=markup)
    elif splited_data[0] == 'edit_name':
        bot.set_state(call.from_user.id, 'edit name')
        selected_todo = get_todo_from_callback(int(splited_data[1]), user[0].user_id, todo_list)
        bot.send_message(call.message.chat.id, 'Введите новое название')
        state = 'edit_name'
        todo = selected_todo
        todo.state = state
        ToDo.update_state_todo(todo.get_id(), state)
    elif splited_data[0] == 'edit_datetime':
        bot.set_state(call.from_user.id, 'edit datetime')
        selected_todo = get_todo_from_callback(int(splited_data[1]), user[0].user_id, todo_list)
        bot.send_message(call.message.chat.id, 'Введите обновленные дату и время')
        state = 'edit_datetime'
        todo = selected_todo
        todo.state = state
        ToDo.update_state_todo(todo.get_id(), state)
    elif splited_data[0] == 'delete':
        selected_todo = get_todo_from_callback(int(splited_data[1]), user[0].user_id, todo_list)
        bot.send_message(call.message.chat.id, 'Напоминание удалено')
        schedule.remove_job(selected_todo.get_id())
        ToDo.delete_todo(selected_todo.get_id(), selected_todo)


@bot.message_handler()
def chat_actions_handler(message):
    user = User.get(message.from_user.id)
    todo_list = ToDo.get(user[0].user_id)
    last_user_todo = todo_list[-1]
    if last_user_todo.state == 'create_name':
        name_of_todo = message.text
        bot.send_message(message.chat.id, """Когда нужно напомнить?\n
(24 февраля в 13:00 | сегодня/завтра в 13:00)""", parse_mode='html')
        state = 'create_date'
        last_user_todo.state = state
        last_user_todo.name_of_todo = name_of_todo
        ToDo.update_todo(last_user_todo.get_id(), name_of_todo, '', state, last_user_todo)
    elif last_user_todo.state == 'create_date':
        parsed_text = parser(message.text)
        if not parsed_text:
            return bot.send_message(message.chat.id, """Некорректный формат ввода или дата \n
Введите обновленные дату и время""", parse_mode='html')
        bot.send_message(message.chat.id, 'Напоминание создано', parse_mode='html')
        state = 'default'
        last_user_todo.date_of_todo = parsed_text
        last_user_todo.state = state
        ToDo.update_todo(last_user_todo.get_id(), last_user_todo.name_of_todo, parsed_text, state, last_user_todo)
        bot.set_state(message.from_user.id, state)
        schedule.add_job(send_notification, 'date', run_date=parsed_text,
                         args=[last_user_todo, message.chat.id], id=f'{last_user_todo.get_id()}')
        if not schedule.state:
            schedule.start()
    elif last_user_todo.state == 'edit_name':
        state = 'default'
        last_user_todo.state = state
        last_user_todo.name_of_todo = message.text
        ToDo.update_todo(last_user_todo.get_id(), message.text, last_user_todo.date_of_todo, state, last_user_todo)
        bot.send_message(message.chat.id, 'Название изменено', parse_mode='html')
        bot.set_state(message.from_user.id, state)
    elif last_user_todo.state == 'edit_datetime':
        parsed_text = parser(message.text)
        if not parsed_text:
            return bot.send_message(message.chat.id, """Неверный формат ввода\n
        Введите обновленные дату и время""", parse_mode='html')
        state = 'default'
        last_user_todo.date_of_todo = parsed_text
        last_user_todo.state = state
        ToDo.update_todo(last_user_todo.get_id(), last_user_todo.name_of_todo, parsed_text, state, last_user_todo)
        bot.send_message(message.chat.id, 'Дата и время изменены', parse_mode='html')
        bot.set_state(message.from_user.id, state)


def send_notification(todo: ToDo, chat_id: int):
    bot.send_message(chat_id, f"""Напоминание\n
{todo.name_of_todo}""", parse_mode='html')
    ToDo.delete_todo(todo.get_id(), todo)


bot.infinity_polling()
