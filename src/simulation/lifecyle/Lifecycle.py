import random

from src.simulation.state.FailureMode import FailureMode
from src.simulation.entities.ProductType import ProductType
from src.simulation.lifecyle.LifecycleBehavior import LifeCycleBehavior

class Lifecycle(LifeCycleBehavior):


    def __init__(self, 
                 type: str,
                 tool_wear: int,
                 machine_failure: int,
                 failure_modes,
                 ):
        
        self._type = ProductType(type)
        self._tool_wear = tool_wear
        self._machine_failure = machine_failure 
        self._failure_modes = failure_modes

    def update_twf(self):
        super().update_twf(self)
        if self._type == ProductType.LOW:
             # Low 等級每秒老化 3 分鐘，極速逼近危險區
            self._tool_wear += 3
        elif self._type == ProductType.MEDIUM:
            # Medium 等級每秒老化 2 分鐘
            self._tool_wear += 2 
        elif self._type == ProductType.HIGH:
            # High 等級最耐磨，每秒僅老化 1 分鐘
            self._tool_wear += 1

        if self._tool_wear < 200:
            self._failure_modes["TWF"] = 0
            self.log = f"🟢 刀具正常運轉中 | 累積磨損: {self.tool_wear_min} 分鐘"
        elif 200 <= self.tool_wear_min <= 240:
            if self.type == 'L':
                 # 3.5% 高風險
                drop_chance = 0.0350 
            elif self.type == 'M':
                 # 1.37% 標準風險
                drop_chance = 0.0137 
            elif self.type == 'H':
                 # 0.5% 低風險
                drop_chance = 0.0050
            
            # 執行每秒降落抽籤
            if random.random() < drop_chance:
                self.failure_modes["TWF"] = 1
                self.machine_failure = 1
                self.log = f"🚨 設備崩潰當機！[{self.type}級] 刀具在第 {self.tool_wear_min} 分鐘發生 TWF 斷裂！"
            else:
                self.log = f"⚠️ [老化高危區] [{self.type}級] 磨損: {self.tool_wear_min} 分鐘 (本秒安全渡過)"

        elif self.tool_wear_min > 240:
            # 在此狀態下，TWF機率不再適用（因為沒在40分鐘內斷裂），但刀具已經徹底鈍化
            self.log = f"⚡ 嚴重超期服役！[{self.type}級] 累積磨損已達 {self.tool_wear_min} 分鐘！隨機崩潰風險極高！"

        

    def is_machine_failure(self):
        return self.machine_failure == 1

        


    
