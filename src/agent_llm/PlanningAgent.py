from src.agent_llm.KnowledgeAgent import KnowledgeAgent
from src.simulation.lifecyle.Lifecycle import Lifecycle

class PlanningAgent:

    def __init__(self, knowledge_agent: KnowledgeAgent):
        self.__knowledge_agent = knowledge_agent

    def repair(self, lifecycle_instance: Lifecycle, ml_prob: float):

        recipe = self.__knowledge_agent.evaluate_diagnose(
            product_type=lifecycle_instance._type,
            air_temp=lifecycle_instance._air_temp,
            process_temp=lifecycle_instance._process_temp,
            speed=lifecycle_instance._rotational_speed,
            torque=lifecycle_instance._torque,
            tool_wear=lifecycle_instance._tool_wear,
            ml_probs=ml_prob
        )

        if recipe["Speed_Delta"] != 0.0:
            lifecycle_instance._rotational_speed += recipe["Speed_Delta"]
        if recipe["Torque_Delta"] != 0.0:
            lifecycle_instance._torque += recipe["Torque_Delta"]
        if recipe["Tool_Wear_Delta"] != 0.0:
            lifecycle_instance._tool_wear += recipe["Tool_Wear_Delta"]

        return recipe["Log"]