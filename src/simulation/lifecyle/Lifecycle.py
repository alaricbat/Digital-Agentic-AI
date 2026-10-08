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
            self.__writer.write(f"🟢 [NORMAL]: 刀具正常運轉中 | 累積磨損: {self._tool_wear} 分鐘")
            self.__writer.write("🟢 [NORMAL]: 刀具處於健康或正常的消耗階段，累計加工時間（Tool Wear）在安全壽命範圍內（未達變換閾值）。")
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
                self._failure_modes[FailureMode.TWF] = 1
                self._machine_failure = 1
                self.__writer.write(f"🚨 [CRITICAL]: 設備崩潰當機！[{self._type}級] 刀具在第 {self._tool_wear} 分鐘發生 TWF 斷裂！")
                self.__writer.write(f"🚨 [CRITICAL]: 刀具壽命耗盡。 刀具累計加工時間已經達到或超過設定的磨損極限（通常在 200 到 240 分鐘之間），必須停機更換刀具，否則會損壞工件。")
            else:
                self.__writer.write(f"⚠️ [WARNING]: [老化高危區] [{self._type}級] 磨損: {self._tool_wear} 分鐘 (本秒安全渡過)")

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
            self.__writer.write(f"🚨 [CRITICAL]: 設備 {self._product_id}: 損壞！原因: HDF熱崩潰")
            self.__writer.write(f"🚨 [CRITICAL]: 熱量淤積，機器過熱。 當環境溫度與製程溫度的差值小於 8.6 K，且主軸轉速低於 1380 rpm 時，代表散熱效能嚴重不足，系統觸發過熱告警。")
        elif is_warning:
            self.__writer.write(f"⚠️ [WARNING]: 設備老化中，請用戶安排『更換設備』！(當前轉速:{round(self.speed,1)}, 溫差:{round(temp_diff,1)})")
        else:
            self.__writer.write("🟢 [NORMAL]: 機器製程產生的熱量能正常發散。環境溫度與機器內部製程溫度的差值保持在正常區間內（大於 8.6 K），且主軸轉速正常。")



    def update_pwf(self):

        super().update_pwf()

        self._torque += self.__torque_rise

        current_power = self._torque * ((self._rotational_speed * 2 * np.pi) / 60.0)

        is_pwf = (current_power < 3500.0) or (current_power > 9000.0)
        is_warning = (current_power < self.__pwf_low_warn) or (current_power > self.__pwf_high_warn)

        if is_pwf:
            self._failure_modes[FailureMode.PWF] = 1
            self._machine_failure = 1
            self.__writer.write(f"🚨 [CRITICAL]: 設備 {self._product_id}: 損壞！原因: PWF功率異常")
            self.__writer.write(f"🚨 [CRITICAL]: 負載異常或動力不足。 當轉速與扭矩的乘積（即機械功率低於 3500 W 或高於 9000 W 時触发。可能代表馬達卡死（高功率）或空轉、失去動力（低功率）。")
        elif is_warning:
            self.__writer.write(f"⚠️ [WARNING]: 設備老化中，請用戶安排『更換設備』！(原因: 功率逼近極限 當前功率: {round(current_power, 1)}W)")
        else:
            self.__writer.write(f"🟢 [NORMAL]: 機器的驅動系統運作正常。製程所需的扭矩（Torque）與主軸轉速（Rotational Speed）搭配合理，實際消耗功率在額定範圍內（介於 3500 W 到 9000 W 之間）。")
        


    def update_osf(self):

        super().update_osf()

        current_osf_load = self._tool_wear * self._torque
        osf_dead = current_osf_load > self.__osf_deadline
        osf_warning = current_osf_load > self.__osf_warn

        if osf_dead:
            self._failure_modes[FailureMode.OSF] = 1
            self._machine_failure = 1
            self.__writer.write(f"🚨 [CRITICAL]: 設備 {self._product_id}: 損壞！原因: OSF過載")
            self.__writer.write(f"🚨 [CRITICAL]: 結構過度受力變形。 這受刀具磨損和扭矩的共同影響。當「刀具磨損時間 (times) 實際扭矩」的乘積超過資料集設定的硬性極限（例如特定機型超過 11,000 或 12,000）時触发，代表機器正在硬碰硬、過度硬撐，隨時可能斷刀或結構變形。")
        elif osf_warning:
            self.__writer.write(f"⚠️ [WARNING]: 設備老化中，請用戶安排『更換設備』！(原因: 刀具與結構過載 當前功率: {round(current_osf_load, 1)}W)")
        else: 
            self.__writer.write(f"🟢 [NORMAL]: 機器承受的機械應力（應變）在結構設計的安全結構範圍內，加工負荷適中。")           


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
            self.__writer.write(f"🚨 [CRITICAL]: 設備 {self._product_id}: 損壞！原因: RNF隨機突發故障")
            self.__writer.write(f"🚨 [CRITICAL]: 未知隨機異常。 此狀態完全不取決於任何機器的運作參數。它代表突發性、不可預測的外部事件（如：突然停電、環境劇烈震動、人為誤觸等）。在資料集中，每台機器不論狀態如何，都有固定約 0.1% 的極低機率被隨機分配到這個告警。")
        elif rnf_warning:
            self.__writer.write(f"⚠️ [WARNING]: 設備老化中，請用戶安排『更換設備』！(原因: 突發訊號抖動頻繁)")
        else: 
            self.__writer.write(f"🟢 [NORMAL]: 機器各項物理參數（溫度、轉速、扭矩）皆正常，且沒有遭遇外部突發干擾。")  
    

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
        


    
