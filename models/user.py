import db.db_handler as db


class User:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_user(self):
        user_row = db.db_select_user(self.user_id)
        if user_row is not None:
            return self
        else:
            return None

    def get_user_todos(self):
        return db.db_select_all_users_todo(self.user_id)

    @staticmethod
    def insert_user(user_id: int):
        return db.db_insert_user(user_id)
