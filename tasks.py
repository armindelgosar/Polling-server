from decorators import str_as_int
from enums import TaskType


class Task:

    def __init__(self, exec_time: int, ttype: TaskType):
        self.execution_time = exec_time
        self.type = ttype


class PeriodicTask(Task):
    _TASK_ID = 0

    @classmethod
    def _get_id(cls):
        cls._TASK_ID += 1
        return cls._TASK_ID

    @str_as_int
    def __init__(self, period: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = period
        self.deadline = period
        self.id = self.__class__._get_id()


class AperiodicTask(Task):
    _TASK_ID = 0

    @classmethod
    def _get_id(cls):
        cls._TASK_ID += 1
        return cls._TASK_ID

    @str_as_int
    def __init__(self, arrival_time: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arrival_time = arrival_time
        self.id = self.__class__._get_id()


class ServerTask(Task):
    @str_as_int
    def __init__(self, period: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.period = period
