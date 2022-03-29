import db.db_handler as db


class ToDo:
    instances = []

    def __init__(self, **kwargs):
        self.__id = kwargs.get('id', None)
        self.name_of_todo = kwargs.get('name_of_todo', None)
        self.date_of_todo = kwargs.get('date_of_todo', None)
        self.user_id = kwargs.get('user_id')
        self.state = kwargs.get('state', 'create_name')
        ToDo.instances.append(self)

    def get_id(self):
        return self.__id

    def create_todo(self):
        created_todo_id = db.db_insert_todo(self.user_id, self.name_of_todo, self.date_of_todo)
        self.__id = created_todo_id

    @staticmethod
    def get_last_todo(user_id: int):
        return db.db_select_last_todo(user_id)

    @staticmethod
    def get_todo(user_id: int, name_of_todo: str, date_of_todo: str):
        return db.db_select_todo(user_id, name_of_todo, date_of_todo)

    @staticmethod
    def update_todo(todo_id: int, name_of_todo: str, datetime: str, state: str, instance: object):
        index_of_instance = ToDo.instances.index(instance)
        ToDo.instances[index_of_instance] = instance
        db.db_update_user_todo(todo_id, name_of_todo, datetime, state)

    @staticmethod
    def update_state_todo(todo_id: int, state: str):
        db.db_update_todo_state(todo_id, state)

    @staticmethod
    def delete_todo(todo_id: int, instance: object):
        ToDo.instances.remove(instance)
        db.db_delete_user_todo(todo_id)

    @classmethod
    def get(cls, user_id: int):
        return [inst for inst in cls.instances if inst.user_id == user_id]

    @classmethod
    def db_sync(cls, user_id: int):
        todos = db.db_select_user_todos(user_id)
        for todo in todos:
            cls(id=todo[0], user_id=todo[1], name_of_todo=todo[2], date_of_todo=todo[3], state=todo[4])
