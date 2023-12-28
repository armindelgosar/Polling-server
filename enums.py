from enum import Enum


class TaskType(Enum):
    PERIODIC = "per"
    APERIODIC = "aper"
    SERVER = "ser"
