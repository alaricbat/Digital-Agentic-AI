import time
import random
import numpy as np
import threading

from src.simulation.state.FailureMode import FailureMode
from src.simulation.entities.ProductType import ProductType
from src.simulation.lifecyle.LifecycleBehavior import LifeCycleBehavior
from src.utils.Writer import Writer

class Lifecycle(LifeCycleBehavior, threading.Thread):

    def __init__(self,
                 product_id: str, 
                 type: str,
                 tool_wear: int,
                 machine_failure: int,
                 failure_modes,
                 air_temp: float,
                 process_temp: float,
                 rotational_speed: int,
                 torque: float,
                 ):

        threading.Thread.__init__(self)

        self.__file_root_log = "src/simulation/logs/"

        self._product_id = product_id
        self._type = ProductType(type)
        self._tool_wear = tool_wear
        self._machine_failure = machine_failure 
        self._failure_modes = failure_modes
        self._air_temp = air_temp
        self._process_temp = process_temp
        self._rotational_speed = rotational_speed
        self._torque = torque

        self.__warn_rotational_speed = 1390
        self.__warn_temp_diff = 9.0
        self.__pwf_low_warn = 3600.0
        self.__pwf_high_warn = 8800.0
        self.__rng = np.random.default_rng(42) #設定隨機數種子
        self.__rnf_instability_score = 0.0 #隨機不穩定度累積

        self.__writer = Writer(tid=threading.get_ident(), 
                               file_path=self.__file_root_log,
                               file_name=self._product_id)

        #根據【L】【M】【H】定義不同每秒老化失落速度
        if self._type == ProductType.LOW:
            self.__speed_drop_per_sec = 0.6
            self.__process_temp_drop_rate = 0.01
            self.__torque_rise = 0.12
            self.__osf_deadline = 11000.0
            self.__osf_warn = 9500.0  
        elif self._type == ProductType.MEDIUM:
            self.__speed_drop_per_sec = 0.3
            self.__process_temp_drop_rate = 0.005
            self.__torque_rise = 0.05
            self.__osf_deadline = 12000.0
            self.__osf_warn = 11200.0
        else:
            self.__speed_drop_per_sec = 0.1
            self.__process_temp_drop_rate = 0.002
            self.__torque_rise = 0.02
            self.__osf_deadline = 13000.0
            self.__osf_warn = 12500.0  



    def update_twf(self):
        super().update_twf()

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
            self.__writer.write(f"🟢 刀具正常運轉中 | 累積磨損: {self._tool_wear} 分鐘")
        elif 200 <= self._tool_wear <= 240:
            if self._type == ProductType.LOW:
                 # 3.5% 高風險
                drop_chance = 0.0350 
            elif self._type == ProductType.MEDIUM:
                 # 1.37% 標準風險
                drop_chance = 0.0137 
            elif self._type == ProductType.HIGH:
                 # 0.5% 低風險
                drop_chance = 0.0050
            
            # 執行每秒降落抽籤
            if random.random() < drop_chance:
                self.failure_modes[FailureMode.TWF] = 1
                self._machine_failure = 1
                self.__writer.write(f"🚨 設備崩潰當機！[{self._type}級] 刀具在第 {self._tool_wear} 分鐘發生 TWF 斷裂！")
            else:
                self.__writer.write(f"⚠️ [老化高危區] [{self._type}級] 磨損: {self._tool_wear} 分鐘 (本秒安全渡過)")

        elif self._tool_wear > 240:
            # 在此狀態下，TWF機率不再適用（因為沒在40分鐘內斷裂），但刀具已經徹底鈍化
            self.__writer.write(f"⚡ 嚴重超期服役！[{self._type}級] 累積磨損已達 {self._tool_wear} 分鐘！隨機崩潰風險極高！")



    def update_hdf(self):

        super().update_hdf()

        # 運行中每秒的物理數值失落更新
        self._rotational_speed -= self.__speed_drop_per_sec
        # 製程溫度往環境溫度附近 （代表散熱不及，溫差正常縮小）
        self._process_temp -= self.__process_temp_drop_rate
        temp_diff = self._process_temp - self._air_temp
        is_hdf = (temp_diff < 8.6) and (self._rotational_speed < 1380)
        is_warning = (temp_diff < self.__warn_temp_diff) and (self._rotational_speed < self.__warn_rotational_speed)

        if is_hdf:
            self._failure_modes[FailureMode.HDF] = 1
            self._machine_failure = 1
            self.__writer.write(f"💥 [CRITICAL] 設備 {self._product_id}: 損壞！原因: HDF熱崩潰")
        elif is_warning:
            self.__writer.write(f"⚠️ WARNING: 設備老化中，請用戶安排『更換設備』！(當前轉速:{round(self.speed,1)}, 溫差:{round(temp_diff,1)})")
        else:
            self.__writer.write("🟢 NORMAL: 設備運行良好")



    def update_pwf(self):

        super().update_pwf()

        self._torque += self.__torque_rise

        current_power = self._torque * ((self._rotational_speed * 2 * np.pi) / 60.0)

        is_pwf = (current_power < 3500.0) or (current_power > 9000.0)
        is_warning = (current_power < self.__pwf_low_warn) or (current_power > self.__pwf_high_warn)

        if is_pwf:
            self._failure_modes[FailureMode.PWF] = 1
            self._machine_failure = 1
            self.__writer.write(f"💥 [CRITICAL] 設備 {self._product_id}: 損壞！原因: PWF功率異常")
        elif is_warning:
            self.__writer.write(f"⚠️ WARNING: 設備老化中，請用戶安排『更換設備』！(原因: 功率逼近極限 當前功率: {round(current_power, 1)}W)")
        else:
            self.__writer.write(f"🟢 NORMAL: 設備運行良好")
        


    def update_osf(self):

        super().update_osf()

        current_osf_load = self._tool_wear * self._torque
        osf_dead = current_osf_load > self.__osf_deadline
        osf_warning = current_osf_load > self.__osf_warn

        if osf_dead:
            self._failure_modes[FailureMode.OSF] = 1
            self._machine_failure = 1
            self.__writer.write(f"💥 [CRITICAL] 設備 {self._product_id}: 損壞！原因: OSF過載")
        elif osf_warning:
            self.__writer.write(f"⚠️ WARNING: 設備老化中，請用戶安排『更換設備』！(原因: 刀具與結構過載 當前功率: {round(current_osf_load, 1)}W)")
        else: 
            self.__writer.write(f"🟢 NORMAL: 設備運行良好")           


    def update_rnf(self):

        super().update_rnf()

        random_roll = self.__rng.random()
        rnf_dead = (random_roll < 0.001)
        if random_roll < 0.05:
            self.__rnf_instability_score += 1.5
        else:
            self.__rnf_instability_score = max(0.0, self.__rnf_instability_score - 0.2) # 沒事的話會慢慢自我修復
        rnf_warning = self.__rnf_instability_score > 3.0

        if rnf_dead:
            self._failure_modes[FailureMode.RNF] = 1
            self._machine_failure = 1  
            self.__writer.write(f"💥 [CRITICAL] 設備 {self._product_id}: 損壞！原因: RNF隨機突發故障")
        elif rnf_warning:
            self.__writer.write(f"⚠️ WARNING: 設備老化中，請用戶安排『更換設備』！(原因: 突發訊號抖動頻繁)")
        else: 
            self.__writer.write(f"🟢 NORMAL: 設備運行良好")  
    

    def is_machine_failure(self):
        return self._machine_failure == 1

    def run(self):

        self._is_running = True

        self.__writer.write(f"▶️ 設備 {self._product_id} 異步生命週期運轉常駐程式啟動")

        while self._is_running:

            self.update_twf()

            self.update_hdf()

            self.update_osf()

            self.update_pwf()

            self.update_rnf()

            if self.is_machine_failure():
                self.__writer.write("🛑 設備已宣告損壞，自動終止後台更新執行緒。")
                self._is_running = False
                break

            time.sleep(1)
        

    def stop(self):
        self._is_running = False
        


    
