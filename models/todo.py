import db.db_handler as db


class ToDo:
    def __init__(self, name_of_todo: str, user_id: int = None, date_of_todo: str = None):
        self.name_of_todo = name_of_todo
        self.date_of_todo = date_of_todo
        self.user_id = user_id

    def create_todo(self):
        db.db_insert_todo(self.user_id, self.name_of_todo, self.date_of_todo)

    @staticmethod
    def get_todo(user_id: int, name_of_todo: str, date_of_todo: str):
        return db.db_select_todo(user_id, name_of_todo, date_of_todo)

    @staticmethod
    def update_todo(todo_id: int, name_of_todo: str, datetime: str):
        db.db_update_user_todo(todo_id, name_of_todo, datetime)

    @staticmethod
    def delete_todo(todo_id: int):
        db.db_delete_user_todo(todo_id)
