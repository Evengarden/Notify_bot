import sqlite3

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()


def db_insert_user(user_id: int):
    cursor.execute('INSERT INTO user (user_id) VALUES (?)', (user_id,))
    conn.commit()


def db_select_user(user_id: int):
    cursor.execute('Select * from user where user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row


def db_insert_todo(user_id: int, name_of_todo: str, date_of_todo: str):
    cursor.execute('INSERT INTO todo (user_id, name_of_todo, date_of_todo) VALUES (?,?,?)',
                   (user_id, name_of_todo, date_of_todo))
    conn.commit()


def db_update_user_todo(todo_id: int, name_of_todo: str, date_of_todo: str):
    cursor.execute('Update todo set name_of_todo = ? , date_of_todo = ? where id = ?',
                   (name_of_todo, date_of_todo, todo_id))
    conn.commit()


def db_select_all_users_todo(user_id: int):
    cursor.execute('Select name_of_todo, date_of_todo from todo where user_id = ?', (user_id,))
    rows = cursor.fetchall()
    return rows


def db_select_todo(user_id: int, name_of_todo: str, date_of_todo: str):
    cursor.execute('Select * from todo where user_id = ? AND name_of_todo = ? AND date_of_todo = ?',
                   (user_id, name_of_todo, date_of_todo))
    row = cursor.fetchone()
    return row


def db_delete_user_todo(todo_id: int):
    cursor.execute('Delete from todo where id = ?', (todo_id,))
    conn.commit()
