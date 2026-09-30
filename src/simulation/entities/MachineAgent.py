import collections
from src.simulation.state.State import State

class MachineAgent:

    def __init__(self, machine_id):
        self.id = machine_id
        self.name = f"Machine_{machine_id}"
        
        # 狀態同步 (State Synchronization)
        self.state = State.IDLE
        
        # 每台機器專屬的暫存緩衝區 (Buffer)
        self.buffer = collections.deque()
        
        # 虛擬感測器數據 (用基礎溫度 25.0 度初始化)
        self.temperature = 25.0