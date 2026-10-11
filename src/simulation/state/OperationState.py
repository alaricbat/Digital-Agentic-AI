from enum import Enum

class OperationState(Enum):
    NORMAL = 'NORMAL'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'