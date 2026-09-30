import random
from src.simulation.engine.FactorySimulation import FactorySimulation
from src.simulation.event.Event import Event
from src.simulation.event.EventType import EventType

def main():
    # Initialize Agent Core
    print("Hello Agent! 2026 I'm here in Taiwan to get the permanent success.")

if __name__ == "__main__":

    main()
    
    random.seed(42)

    factory = FactorySimulation(num_machines=2)

    for i in range(1, 6):
        arrival_time = i * 4.0
        target_machine = (i % 2) 
        factory.queue.push(Event(time=arrival_time, event_type=EventType.JOB_ARRIVAL, machine_id=target_machine, job_id=100+i))

    factory.run(max_sim_time=60.0)
