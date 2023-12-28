import random
from typing import Dict, List

from tasks import *
import matplotlib.pyplot as plt


class ExternalIntegrator:
    TYPE_TASK_CREATOR_MAPPER = {
        TaskType.SERVER.value: ServerTask,
        TaskType.PERIODIC.value: PeriodicTask,
        TaskType.APERIODIC.value: AperiodicTask,
    }

    @classmethod
    def create_tasks(cls, file_name: str):
        with open(f"samples/{file_name}", "r") as sample:
            data = sample.read().split("\n")
            tasks = data[:-1]
            end_time = int(data[-1])
            return [cls._generate_task(*task.split()) for task in tasks], end_time

    @classmethod
    def _generate_task(cls, ttype, *args):
        return cls.TYPE_TASK_CREATOR_MAPPER.get(ttype)(*args, ttype)

    @classmethod
    def display_report(cls, report_data: dict):
        diagram_count = len({report_data[i].get("id") for i in report_data} - {None})
        cat_data = cls._categorize_data(report_data)
        end_time = max(report_data.keys()) + 1

        fig, axs = plt.subplots(diagram_count, 1, figsize=(10, 4), sharex=True)
        cls._generate_aperiodic_diagram_data(axs[-2], cat_data.pop(TaskType.APERIODIC.value), end_time)
        cls._generate_periodic_diagram_data(axs[:-2], cat_data, end_time)
        cls._generate_server_charge_diagram_data(axs[-1], report_data, end_time)

        plt.xticks(range(0, 25))
        plt.tight_layout()
        plt.show()

    @staticmethod
    def _categorize_data(data: Dict):
        per_ids = {data[i].get("id") for i in data if data[i].get("type") == TaskType.PERIODIC.value}
        task_data = {TaskType.APERIODIC.value: [], **{i: [] for i in per_ids}}

        for d in data:
            if data[d].get("type") == TaskType.APERIODIC.value:
                task_data[TaskType.APERIODIC.value].append({**data[d], "t": d})
                continue
            cat = data[d].get("id")
            if cat is None:
                continue
            task_data[cat].append({**data[d], "t": d})

        return task_data

    @staticmethod
    def random_color():
        return "#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])

    @classmethod
    def _generate_server_charge_diagram_data(cls, ax, logs: Dict, end_time: int):
        s_charge_values = [logs[t].get("server_charge") for t in logs]
        t_values = list(logs.keys())
        color = cls.random_color()
        ax.fill_between(t_values, 0, s_charge_values, color=color, alpha=1)
        for i in range(0, end_time - 1):
            if logs[i].get("idle") or logs[i].get("task_period") > logs[i].get("server_period") or abs(s_charge_values[i + 1] - s_charge_values[i]) == 2:
                ax.fill_between([t_values[i], t_values[i + 1]], 0, [2, 2], color="white", alpha=1)
        ax.set_ylabel('Cs')
        ax.set_xlabel('Time')
        ax.set_ylim(0, 2)

    @classmethod
    def _generate_periodic_diagram_data(cls, axs, logs: Dict, end_time: int):
        random_colors = [cls.random_color() for _ in range(len(logs.keys()))]
        for ax, task in zip(axs, logs):
            color = random_colors[task % len(logs.keys())]
            tlogs = logs[task]
            starts = [log.get("t") for log in tlogs]
            durations = vals = [1 for _ in range(len(starts))]
            for start, duration, value in zip(starts, durations, vals):
                ax.bar(start, value, duration, align='edge', edgecolor='grey', fill=True, color=color)
            ax.set_ylabel(f'τ{task}')
            ax.set_xlim(0, end_time)
            ax.set_ylim(0, 1)
            ax.set_xticks(range(0, 25))
            ax.grid(True, which='both', axis='x', linestyle='--', linewidth=1)

    @classmethod
    def _generate_aperiodic_diagram_data(cls, ax, logs: List, end_time: int):
        task_count = max(logs, key=lambda x: x.get("id"))["id"]
        random_colors = [cls.random_color() for _ in range(task_count)]
        ids = [log.get("id") for log in logs]
        starts = [log.get("t") for log in logs]
        durations = vals = [1 for _ in range(len(starts))]

        for start, duration, value, iid in zip(starts, durations, vals, ids):
            ax.bar(start, value, duration, align='edge', edgecolor='grey', fill=True,
                   color=random_colors[iid % task_count])

        ax.set_ylabel('Aperiodic Requests')
        ax.set_xlim(0, end_time)
        ax.set_ylim(0, 1)
        ax.set_xticks(range(0, 25))
        ax.grid(True, which='both', axis='x', linestyle='--', linewidth=1)
