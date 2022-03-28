import telebot
from src.parser import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from telebot import types
from models.user import User
from models.todo import ToDo

import cfg

bot = telebot.TeleBot(cfg.API_TOKEN)

schedule = BlockingScheduler()

global state, user, chat_id, todo_list, todo, dict_todo_list
state = 'default'
user = object
todo = object
chat_id = 0
todo_list = []
dict_todo_list = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global user
    bot.reply_to(message, """\
    Привет! Я NotifyBot.
Я буду помогать тебе не забыть важные события или дела, которые необходимо сделать!\
 Для получения доступного списка команд введи /help
    """)
    current_user = User(message.from_user.id)
    if current_user.get_user() is None:
        User.insert_user(message.from_user.id)
    else:
        current_user = current_user.get_user()
    user = current_user


@bot.message_handler(commands=['help'])
def get_commands_list(message):
    bot.reply_to(message, """\
    /start - старт бота.
/add - добавить событие.
/list - получить список событий
        """)


@bot.message_handler(commands=['add'])
def add_todo(message):
    bot.send_message(message.chat.id, 'О чем нужно напомнить?', parse_mode='html')
    global state, chat_id
    state = 'create_name'
    chat_id = message.chat.id


@bot.message_handler(commands=['list'])
def get_todo_list(message):
    global user, todo_list, dict_todo_list
    markup = types.InlineKeyboardMarkup()
    todo_list = user.get_user_todos()
    dict_todo_list = dict(todo_list)
    for key in dict_todo_list:
        markup.add(types.InlineKeyboardButton(f"{key} в {dict_todo_list[key]}",
                                              callback_data=f"{key}"))
    bot.send_message(message.chat.id, 'Список напоминаний', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    global state, dict_todo_list, todo
    if call.data in dict_todo_list:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Изменить название", callback_data='edit_name'))
        markup.add(types.InlineKeyboardButton("Изменить дату и время", callback_data='edit_datetime'))
        markup.add(types.InlineKeyboardButton("Удалить", callback_data='delete'))
        todo = ToDo.get_todo(user.user_id, call.data, dict_todo_list[call.data])
        bot.send_message(call.message.chat.id, 'Что нужно сделать с напоминанием?', reply_markup=markup)
    elif call.data == 'edit_name':
        bot.send_message(call.message.chat.id, 'Введите новое название')
        state = 'edit_name'
    elif call.data == 'edit_datetime':
        bot.send_message(call.message.chat.id, 'Введите обновленные дату и время')
        state = 'edit_datetime'
    elif call.data == 'delete':
        bot.send_message(call.message.chat.id, 'Напоминание удалено')
        ToDo.delete_todo(todo[0])


@bot.message_handler()
def chat_actions_handler(message):
    global state, todo
    name_of_todo = ''
    current_state = state
    if current_state == 'create_name':
        name_of_todo = message.text
        todo = ToDo(name_of_todo)
        bot.send_message(message.chat.id, """Когда нужно напомнить?\n
(24 февраля в 13:00 | сегодня/завтра в 13:00)""", parse_mode='html')
        state = 'create_date'

    elif current_state == 'create_date':
        parsed_text = parser(message.text)
        if not parsed_text:
            return bot.send_message(message.chat.id, """Неверный формат ввода\n
Введите обновленные дату и время""", parse_mode='html')
        todo.date_of_todo = parsed_text
        todo.user_id = user.user_id
        bot.send_message(message.chat.id, 'Напоминание создано', parse_mode='html')
        todo.create_todo()
        schedule.add_job(send_notification, 'date', run_date=parsed_text, args=[todo.name_of_todo])
        state = 'default'
        if not schedule.state:
            schedule.start()
    elif current_state == 'edit_name':
        ToDo.update_todo(todo[0], message.text, todo[3])
        bot.send_message(message.chat.id, 'Название изменено', parse_mode='html')
    elif current_state == 'edit_datetime':
        parsed_text = parser(message.text)
        if not parsed_text:
            return bot.send_message(message.chat.id, """Неверный формат ввода\n
        Введите обновленные дату и время""", parse_mode='html')
        ToDo.update_todo(todo[0], todo[2], parsed_text)
        bot.send_message(message.chat.id, 'Дата и время изменены', parse_mode='html')


def send_notification(name: str):
    global user, dict_todo_list
    bot.send_message(chat_id, f"""Напоминание\n
{name}""", parse_mode='html')
    completed_todo = ToDo.get_todo(user.user_id, name, dict_todo_list[name])
    ToDo.delete_todo(completed_todo[0])


bot.infinity_polling()
