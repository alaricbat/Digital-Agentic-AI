import numpy as np
import pandas as pd

from src.simulation.event.Event import Event
from src.simulation.event.EventType import EventType
from src.simulation.event.EventQueue import EventQueue
from src.simulation.entities.MachineAgent import MachineAgent

from src.simulation.state.State import State

class FactorySimulation:

    def __init__(self, num_machines):

        # 核心模擬時鐘 (Simulation Clock)
        self.sim_clock = 0.0
        # 核心事件佇列 (Event Queue)
        self.queue = EventQueue()

        # 初始化工廠內的所有機器 Agent
        self.num_machines = num_machines
        self.machines = {i: MachineAgent(machine_id=i) for i in range(num_machines)}

        # 用於存儲歷史數據的列表，最後交給 pandas 轉換成 CSV
        self.history_logs = []

    def update_sensors(self):

        # 1. 提取所有機器的當前狀態與溫度
        states = np.array([self.machines[i].state for i in range(self.num_machines)])
        temps = np.array([self.machines[i].temperature for i in range(self.num_machines)])

        # 2. 建立狀態遮罩
        processing_mask = (states == State.PROCESSING)
        idle_mask = (states == State.IDLE)

        # 3. 加工中的機器升溫，閒置的機器降溫
        temps[processing_mask] += np.random.uniform(low=1.5, high=3.5, size=np.sum(processing_mask))
        temps[idle_mask] -= (temps[idle_mask] - 25.0) * 0.1

        # 4. 確保溫度不會低於室溫，並同步回機器 Agent
        temps = np.maximum(25.0, temps)
        for i in range(self.num_machines):
            self.machines[i].temperature = temps[i]

    def log_state(self, event_desc):
        
        log_entry = {
            "timestamp": self.sim_clock,
            "event": event_desc
        }

        for i, m in self.machines.items():
            log_entry[f"M{i}_State"] = m.state
            log_entry[f"M{i}_Temp"] = m.temperature
            log_entry[f"M{i}_Buffer_Len"] = len(m.buffer)

        self.history_logs.append(log_entry)

        # 在控制台打印當前實時狀況
        temp_status = [f"{self.machines[i].temperature:.1f}°C" for i in range(self.num_machines)]
        state_status = [self.machines[i].state for i in range(self.num_machines)]
        print(f"[{self.sim_clock:5.1f}] x {event_desc:<22} | 溫度: {temp_status} | 狀態: {state_status}")

    def handle_event(self, event: Event):

        m_id = event.machine_id
        machine = self.machines[m_id]

        if event.event_type == EventType.JOB_ARRIVAL:
            machine.buffer.append(event.job_id)
            self.log_state(f"Job {event.job_id} 到達 M{m_id} 緩衝區")

            if machine.state == State.IDLE:
                self.queue.push(Event(self.sim_clock, EventType.MACHINE_START, m_id))

        elif event.event_type == EventType.MACHINE_START:
            if machine.buffer and machine.state == State.IDLE:
                current_job_id = machine.buffer.popleft()

                machine.state = State.PROCESSING
                self.log_state(f"M{m_id} 開始加工 Job {current_job_id}")

                # 預定完成時間（這裡先固定加工 10 分鐘）
                processing_time = 10.0
                finish_time = self.sim_clock + processing_time

                # 生成加工完成事件
                self.queue.push(Event(finish_time, EventType.MACHINE_FINISH, m_id, current_job_id))

        elif event.event_type == EventType.MACHINE_FINISH:

            machine.state = State.IDLE

            self.log_state(f"M{m_id} 完成加工 Job {event.job_id}")

            # 檢查緩衝區是否還有工件，有的話繼續開工
            if machine.buffer:
                self.queue.push(Event(self.sim_clock, 'MACHINE_START', m_id))

    def run(self, max_sim_time):

        while not self.queue.is_empty():

            current_event = self.queue.pop()

            if current_event.time > max_sim_time:
                break

            self.sim_clock = current_event.time
            self.update_sensors()
            self.handle_event(current_event)

        print("=== 模擬結束 ===")

        df = pd.DataFrame(self.history_logs)
        df.to_csv("data/raw/factory_sensor_data.csv", index=False)
        print(f"成功自主生成數據集，已儲存至 data/raw/factory_sensor_data.csv (共 {len(df)} 筆數據)")
        