import sqlite3

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()


def db_insert_user(user_id: int):
    cursor.execute('INSERT INTO user (user_id) VALUES (?)', (user_id,))
    conn.commit()
    return cursor.lastrowid


def db_select_user(user_id: int):
    cursor.execute('Select * from user where user_id = ?', (user_id,))
    row = cursor.fetchone()
    return row


def db_insert_todo(user_id: int, name_of_todo: str, date_of_todo: str):
    cursor.execute('INSERT INTO todo (user_id, name_of_todo, date_of_todo) VALUES (?,?,?)',
                   (user_id, name_of_todo, date_of_todo))
    conn.commit()
    return cursor.lastrowid


def db_update_user_todo(todo_id: int, name_of_todo: str, date_of_todo: str, state: str):
    cursor.execute('Update todo set name_of_todo = ? , date_of_todo = ?, state = ? where id = ?',
                   (name_of_todo, date_of_todo, state, todo_id))
    conn.commit()


def db_update_todo_state(todo_id: int, state: str):
    cursor.execute('Update todo set state = ? where id = ?',
                   (state, todo_id))
    conn.commit()


def db_select_all_users_todo(user_id: int):
    cursor.execute('Select name_of_todo, date_of_todo from todo where user_id = ?', (user_id,))
    rows = cursor.fetchall()
    return rows


"""Method for sync instances of todo and db"""


def db_select_user_todos(user_id: int):
    cursor.execute('Select * from todo where user_id = ?', (user_id,))
    rows = cursor.fetchall()
    return rows


def db_select_todo(user_id: int, name_of_todo: str, date_of_todo: str):
    cursor.execute('Select * from todo where user_id = ? AND name_of_todo = ? AND date_of_todo = ?',
                   (user_id, name_of_todo, date_of_todo))
    row = cursor.fetchone()
    return row


def db_select_last_todo(user_id: int):
    cursor.execute('Select * from todo where user_id = ? ORDER BY id DESC LIMIT 1',
                   (user_id,))
    row = cursor.fetchone()
    return row


def db_delete_user_todo(todo_id: int):
    cursor.execute('Delete from todo where id = ?', (todo_id,))
    conn.commit()
