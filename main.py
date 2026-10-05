import random

import pandas as pd
import numpy as np

from src.simulation.entities.ProductionAsset import ProductionAsset

DEVICE_SZ = 5

def main():
    # Initialize Agent Core
    print("Hello Agent! 2026 I'm here in Taiwan to get the permanent success.")

if __name__ == "__main__":

    main()

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

    for assets in asset_products:
        assets.start()
