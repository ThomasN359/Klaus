import enum
from datetime import time


class TaskType(enum.Enum):
    ACTIVE = 1
    TIMER = 2
    SUSTAIN = 3
    BEDTIME = 4
# TODO Enum may be removed


class TaskStatus(enum.Enum):
    PENDING = 1
    PASSED = 2
    FAILED = 3
    PLAYING = 4

class AddMethod(enum.Enum):
    MANUAL = 1
    SUNDAY = 2
    MONDAY = 3
    TUESDAY = 4
    WEDNESDAY = 5
    THURSDAY = 6
    FRIDAY = 7
    SATURDAY = 8
    AI = 9


class Task:
    def __init__(self, task_name: str, task_description: str, task_type: TaskType, task_status: TaskStatus, add_method: AddMethod,  lock_in: bool = False):
        self.task_name = task_name
        self.task_description = task_description
        self.task_type = task_type
        self.task_status = task_status
        self.add_method = add_method
        self.lock_in = lock_in

    def display_task_name(self):
        print(f"Task Name: {self.task_name}")
        print(f"Task Description: {self.task_description}")
        print(f"Task Type: {self.task_type.name}")


class ActiveTask(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, add_method: AddMethod, reminder: list[str],
                 due_by: time):
        super().__init__(task_name, task_description, TaskType.ACTIVE, TaskStatus.PENDING, AddMethod.MANUAL)
        self.reminder = reminder
        self.due_by = due_by


class TimerTask(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus,add_method: AddMethod, reminder: list[str],
                 due_by: time, start_by: time, duration: int, app_block_list: str, web_block_list: str):
        super().__init__(task_name, task_description, TaskType.TIMER, TaskStatus.PENDING, AddMethod.MANUAL)
        self.duration = duration
        self.app_block_list = app_block_list
        self.web_block_list = web_block_list
        self.reminder = reminder
        self.due_by = due_by
        self.start_by = start_by



class SustainTask(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, add_method: AddMethod,contract: str, due_by: time):
        super().__init__(task_name, task_description, TaskType.SUSTAIN, TaskStatus.PENDING, AddMethod.MANUAL)
        self.contract = contract
        self.due_by = due_by


class BedTime(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, add_method: AddMethod, due_by: time,
                 reminder: list[str], shutdown: bool):
        super().__init__(task_name, task_description, TaskType.BEDTIME, TaskStatus.PENDING, AddMethod.MANUAL)
        self.due_by = due_by
        self.reminder = reminder
        self.shutdown = shutdown