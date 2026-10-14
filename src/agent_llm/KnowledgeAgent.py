import numpy as np

from src.simulation.entities.ProductType import ProductType
from src.agent_llm.ActionAgent import ActionAgent

class KnowledgeAgent:

    def __init__(self):
        self.__thresholds = {
            ProductType.LOW: {
                "osf_limit": 9500.0,
                "hdf_temp": 9.0,
                "hdf_speed": 1390,
                "power_min": 3600.0,
                "power_max": 8800.0,
                "twf_min": 200
            },
            ProductType.MEDIUM: {
                "osf_limit": 11200.0,
                "hdf_temp": 9.0,
                "hdf_speed": 1390,
                "power_min": 3600.0,
                "power_max": 8800.0,
                "twf_min": 200
            },
            ProductType.HIGH: {
                "osf_limit": 12500.0,
                "hdf_temp": 9.0,
                "hdf_speed": 1390,
                "power_min": 3600.0,
                "power_max": 8800.0,
                "twf_min": 200
            }
        }

    def evaluate_diagnose(self,
                          product_type: ProductType,
                          air_temp: float,
                          process_temp: float,
                          speed: float,
                          torque: float,
                          tool_wear: int,
                          ml_probs: dict):
        manual = self.__thresholds.get(product_type)

        temp_diff = process_temp - air_temp
        current_power = torque * ((speed * 2 * np.pi) / 60.0)
        current_osf_load = torque * tool_wear

        result = {
                "Action": ActionAgent.KEEP_RUNNING,
                "Speed_Delta": 0.0,
                "Torque_Delta": 0.0,
                "Process_Temp_Delta": 0.0,
                "Tool_Wear_Delta": 0,
                "Log": "🟢 [KNOWLEDGE]: 設備各項物理參數與 ML 評估狀態安全，維持基礎生產。\n"
            }

        if ml_probs > 0.45 or current_osf_load > (manual["osf_limit"]):
            reduction_nm = 12.0 if product_type == ProductType.LOW else (8.0 if product_type == ProductType.MEDIUM else 5.0)
            result["Action"] += " " + ActionAgent.STRESS_RELIEF
            result["Speed_Delta"] += 0.0
            result["Torque_Delta"] += -reduction_nm
            result["Process_Temp_Delta"] += 0.0
            result["Tool_Wear_Delta"] += 0
            result["Log"] += f"🛠️ [KNOWLEDGE ACTION -> OSF]: 結構負荷過高({round(current_osf_load, 1)})，已超越你的預警線({manual["osf_limit"]})！採取【應力釋放改修】，強行削減扭矩 {reduction_nm} Nm。\n"
        
        if temp_diff < manual["hdf_temp"] and speed < manual["hdf_speed"]:
            boost_rpm = 250.0 if product_type == ProductType.LOW else 150.0
            temp_compensation = 3.5 if product_type == ProductType.LOW else 2.0
            result["Action"] += " " + ActionAgent.COOLING_COMPENSATION
            result["Speed_Delta"] += boost_rpm
            result["Torque_Delta"] += -2.0
            result["Process_Temp_Delta"] += temp_compensation
            result["Tool_Wear_Delta"] += 0
            result["Log"] += f"🛠️ [KNOWLEDGE ACTION -> HDF]: 溫差過近({round(temp_diff, 2)}K)且主軸低速！採取【熱補償改修】，強制提升轉速 {boost_rpm} rpm 帶動排風散熱。\n"
        
        if current_power < manual["power_min"] or current_power > manual["power_max"]:
            torque_adj = -10.0 if current_power > manual["power_max"] else 5.0
            result["Action"] += " " + ActionAgent.POWER_STABILIZATION
            result["Speed_Delta"] += 0.0
            result["Torque_Delta"] += torque_adj
            result["Process_Temp_Delta"] += 0.0
            result["Tool_Wear_Delta"] += 0
            result["Log"] += f"🛠️ [KNOWLEDGE ACTION -> PWF]: 機械功率異常({round(current_power, 1)}W)！採取【功率穩定改修】，動態調節扭矩 {torque_adj} Nm。\n"

        if tool_wear >= manual['twf_min']:
            result["Action"] += " " + ActionAgent.SCHEDULE_TOOL_CHANGE
            result["Speed_Delta"] += -150.0
            result["Torque_Delta"] += -5.0
            result["Process_Temp_Delta"] += 0.0
            result["Tool_Wear_Delta"] += -150
            result["Log"] += f"🛠️ [KNOWLEDGE ACTION -> TWF]: 刀具超期服役({tool_wear}分鐘)！採取【減速慢行改修】，降速並派發換刀單。\n"

        return result