import db.db_handler as db


class User:
    instances = []

    def __init__(self, **kwargs):
        self.__id = kwargs.get('id', None)
        self.user_id = kwargs.get('user_id')
        User.instances.append(self)

    def get_user(self):
        user_row = db.db_select_user(self.user_id)
        if user_row is not None:
            self.__id = user_row[0]
            return self
        else:
            return None

    def get_user_todos(self):
        created_user = db.db_select_all_users_todo(self.user_id)
        self.__id = created_user

    @staticmethod
    def insert_user(user_id: int, user: object):
        User.instances.append(user)
        return db.db_insert_user(user_id)

    @classmethod
    def get(cls, user_id: int):
        return [inst for inst in cls.instances if inst.user_id == user_id]

    @classmethod
    def db_sync(cls, user_id: int):
        user = db.db_select_user(user_id)
        cls(id=user[0], user_id=user[1])
