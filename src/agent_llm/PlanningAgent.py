
from src.agent_llm.KnowledgeAgent import KnowledgeAgent

class PlanningAgent:

    def __init__(self, knowledge_agent: KnowledgeAgent):
        self.__knowledge_agent = knowledge_agent

    def repair(self, 
               product_type, 
               air_temp,
               process_temp,
               speed,
               torque,
               tool_wear,
               ml_prob: float):

        recipe = self.__knowledge_agent.evaluate_diagnose(
            product_type=product_type,
            air_temp=air_temp,
            process_temp=process_temp,
            speed=speed,
            torque=torque,
            tool_wear=tool_wear,
            ml_probs=ml_prob
        )

        if recipe["Speed_Delta"] != 0.0:
            speed += recipe["Speed_Delta"]
        if recipe["Torque_Delta"] != 0.0:
            torque += recipe["Torque_Delta"]
        if recipe["Process_Temp_Delta"] != 0.0:
            process_temp += process_temp;
        if recipe["Tool_Wear_Delta"] != 0.0:
            tool_wear += recipe["Tool_Wear_Delta"]

        return speed, torque, process_temp, tool_wear, recipe["Log"]