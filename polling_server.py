import math
from functools import cached_property, reduce
from typing import List, Optional, Union
from integrator import ExternalIntegrator
from tasks import *


class Runner:
    def __init__(self):
        self.scheduler = None
        self.end_time = None
        self.tasks = {
            TaskType.SERVER.value: None,
            TaskType.PERIODIC.value: [],
            TaskType.APERIODIC.value: [],
        }

    def _add_init_data(self, data: tuple):
        self._add_tasks(data[0])
        self.end_time = data[1]

    def _add_tasks(self, tasks: List[Task]):
        for task in tasks:
            if self.tasks.get(task.type) is None:
                self.tasks[task.type] = task
            else:
                self.tasks[task.type].append(task)

    def _validate_schedulable(self):
        if not self.end_time == self.scheduler.find_hyper_period():
            print("____HYPER PERIOD IS NOT EQUAL TO GIVEN END TIME___")
            valid = True
        elif not self.scheduler.check_schedulability():
            print("____THESE TASKS ARE NOT SCHEDULABLE!____")
            valid = False
        else:
            print("____TASKS ARE SCHEDULABLE!____")
            valid = True
        return valid

    def run(self, input_path: str):
        self._add_init_data(ExternalIntegrator.create_tasks(input_path))
        self.scheduler = Scheduler(self.tasks, self.end_time)
        if not self._validate_schedulable():
            return
        print("SCHEDULING IS IN PROGRESS...")
        report = self.scheduler.schedule()
        ExternalIntegrator.display_report(report)


class Scheduler:
    class STask:
        def __init__(self, release_time: int, exec_time: int, deadline: Optional[int],
                     task: Union[PeriodicTask, AperiodicTask]):
            self.release_time = release_time
            self.remaining_time = exec_time
            self.deadline = deadline
            self.task = task

        @property
        def period(self):
            if self.task.type == TaskType.PERIODIC.value:
                return self.task.period
            return None

    def __init__(self, tasks: dict, end_time: Optional[int]):
        self.tasks = tasks
        self.end_time = end_time
        self.server_charge = 0

    @cached_property
    def _server(self):
        return self.tasks.get(TaskType.SERVER.value)

    @cached_property
    def _periodic_tasks(self):
        return self.tasks.get(TaskType.PERIODIC.value)

    @cached_property
    def _aperiodic_tasks(self):
        return self.tasks.get(TaskType.APERIODIC.value)

    def check_schedulability(self):
        utility = sum(t.execution_time / t.period for t in self.tasks.get(TaskType.PERIODIC.value)) + \
                  self._server.execution_time / self._server.period
        total_task_count = len(self.tasks.get(TaskType.PERIODIC.value)) + 1
        val = total_task_count * (2 ** (1 / total_task_count) - 1)
        return utility <= val

    def find_hyper_period(self):
        periods = {t.period for t in self._periodic_tasks}
        periods.add(self._server.period)
        return reduce(lambda x, y: x * y // math.gcd(x, y), periods)

    def _add_tasks_to_queue(self, queue: List, time: int):
        for pt in self._periodic_tasks:
            if time == 0 or time % pt.period == 0:
                queue.append(
                    self.STask(release_time=time, exec_time=pt.execution_time, deadline=time + pt.period,
                               task=pt))

        for apt in self._aperiodic_tasks:
            if time == apt.arrival_time:
                queue.append(self.STask(release_time=time, exec_time=apt.execution_time, deadline=None, task=apt))

    def _update_server(self, time: int):
        if time == 0 or time % self._server.period == 0:
            self.server_charge += self._server.execution_time

    def _select_proper_task_to_run(self, queue: List[STask]):
        if not len(queue):
            return None
        queue.sort(key=lambda t: t.period if t.period else self._server.period)

        if len(queue) < 2:
            selected = queue[0]
        elif len(list(filter(
                lambda t: (t.period or self._server.period) == (queue[0].period or self._server.period),
                queue))) > 1:
            selected = min(queue, key=lambda t: t.release_time)
        else:
            selected = queue[0]

        if selected.task.type == TaskType.APERIODIC.value and self.server_charge == 0:
            iterator = iter(queue)
            while nt := next(iterator, None):
                if nt.task.type == TaskType.PERIODIC.value:
                    selected = nt
                    break

        return selected

    def _run_task(self, stask: STask):
        executed = False

        if not stask:
            return executed

        if stask.task.type == TaskType.APERIODIC.value:
            if self.server_charge > 0:
                stask.remaining_time -= 1
                executed = True
        else:
            stask.remaining_time -= 1
            executed = True

        return executed

    def _add_log(self, execution_logger: dict, stask: STask, executed: bool, time: int):
        if not executed:
            log = {
                "server_charge": self.server_charge,
                "idle": True
            }
        else:
            log = {
                "type": stask.task.type,
                "id": stask.task.id,
                "task_period": stask.period or self._server.period,
                "deadline": stask.deadline,
                "release_time": stask.release_time,
                "server_charge": self.server_charge,
                "server_period": self._server.period,
                "idle": False
            }
        execution_logger[time] = log

    def _prune_finished_jobs(self, queue: List):
        return list(filter(lambda t: t.remaining_time > 0, queue))

    def _check_server_usage(self, stask: STask, executed: bool):
        if not executed:
            self.server_charge = 0

        elif stask.task.type == TaskType.APERIODIC.value:
            self.server_charge -= 1

        elif stask.period > self._server.period:
            self.server_charge = 0

    def schedule(self):
        time = 0
        end_time = self.end_time or self.find_hyper_period()
        execution_logger = {}
        queue = []
        while time < end_time:
            self._add_tasks_to_queue(queue, time)
            self._update_server(time)
            selected_task = self._select_proper_task_to_run(queue)
            executed = self._run_task(selected_task)
            queue = self._prune_finished_jobs(queue)
            self._add_log(execution_logger, selected_task, executed, time)
            self._check_server_usage(selected_task, executed)
            time += 1
        return execution_logger


runner = Runner()
runner.run(input_path="1.txt")
