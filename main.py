import random

import pandas as pd
import numpy as np

from src.simulation.engine.FactorySimulation import FactorySimulation
from src.simulation.event.Event import Event
from src.simulation.event.EventType import EventType

from src.simulation.entities.ProductionAsset import ProductionAsset

DEVICE_SZ = 10

def main():
    # Initialize Agent Core
    print("Hello Agent! 2026 I'm here in Taiwan to get the permanent success.")

if __name__ == "__main__":

    main()
    
    # random.seed(42)

    # factory = FactorySimulation(num_machines=2)

    # for i in range(1, 6):
    #     arrival_time = i * 4.0
    #     target_machine = (i % 2) 
    #     factory.queue.push(Event(time=arrival_time, event_type=EventType.JOB_ARRIVAL, machine_id=target_machine, job_id=100+i))

    # factory.run(max_sim_time=60.0)

    df = pd.read_csv('data/raw/ai4i2020.csv')
    df_filtered_products = df.iloc[:DEVICE_SZ, :].to_dict('records')
    asset_products = [
        ProductionAsset(
            udi=product['UDI'], 
            product_id=product['Product ID'],
            type=product['Type'],
            air_temp=product['Air temperature [K]'],
            process_temp=product['Process temperature [K]'],
            rotational_speed=product['Rotational speed [rpm]'],
            torque=product['Torque [Nm]'],
            tool_wear=product['Tool wear [min]'],
            machine_failure=product['Machine failure'],
            twf=product['TWF'],
            hdf=product['HDF'],
            pwf=product['PWF'],
            osf=product['OSF'],
            rnf=product['RNF']
        )
        for product in df_filtered_products
    ]
    print(len(asset_products))
