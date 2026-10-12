# Digital Agentic AI

A Python-based predictive maintenance and digital-twin simulation project that combines an industrial asset lifecycle model with AI-assisted reasoning and rule-based maintenance actions.

This repository explores how an "agentic" workflow can monitor equipment health, detect failure modes, trigger corrective actions, and log diagnostic decisions using the AI4I 2020 Predictive Maintenance dataset.

## Overview

The project models manufacturing equipment as a simulated production asset with multiple failure conditions:

- TWF: Tool Wear Failure
- HDF: Heat Dissipation Failure
- PWF: Power Failure
- OSF: Over-Stress Failure
- RNF: Random Failure

A lightweight AI component loads a LightGBM model from `src/ml_dl/model/lgb_model.txt`, while a knowledge/planning agent interprets sensor conditions and applies corrective changes such as torque reduction, speed adjustment, cooling compensation, and tool replacement scheduling.

## Key Features

- Simulated production asset lifecycle
- Predictive maintenance logic based on sensor readings
- AI model integration using LightGBM
- Failure-mode monitoring and decision rules
- Human-readable runtime logs for diagnostics
- Dataset-driven experimentation with realistic operating conditions

## Repository Structure

```text
Digital-Agentic-AI/
├── data/
│   ├── raw/
│   │   ├── ai4i2020.csv
│   │   └── factory_sensor_data.csv
│   └── operating/
│       └── *.csv
├── notebook/
│   └── Digital_Agentic_AI.ipynb
├── src/
│   ├── agent_llm/
│   │   ├── ActionAgent.py
│   │   ├── KnowledgeAgent.py
│   │   └── PlanningAgent.py
│   ├── optimization/
│   │   ├── mathematical.py
│   │   └── scheduler.py
│   ├── simulation/
│   │   ├── entities/
│   │   ├── lifecyle/
│   │   ├── logs/
│   │   ├── ml/
│   │   └── state/
│   ├── ml_dl/
│   │   └── model/
│   └── utils/
│       └── Writer.py
├── main.py
├── README.md
└── .gitignore
```

## Dataset

The project uses the AI4I 2020 Predictive Maintenance Dataset, which includes operational and failure-related signals such as:

- Air temperature
- Process temperature
- Rotational speed
- Torque
- Tool wear
- Machine failure indicator
- Failure mode flags

These values are loaded from the raw dataset in `data/raw/ai4i2020.csv` and used to create simulated assets.

## Prerequisites

Make sure Python 3.10+ is installed.

Then install the required packages:

```bash
pip install pandas numpy lightgbm
```

## Quick Start

Run the main simulation entry point:

```bash
python main.py
```

The program loads a subset of records from the dataset, creates `ProductionAsset` instances, and runs the lifecycle logic to simulate equipment behavior.

## Example Runtime Flow

1. Read product and machine data from the dataset
2. Instantiate production assets
3. Load the LightGBM model
4. Evaluate sensor conditions and failure likelihood
5. Apply rule-based corrective maintenance plans
6. Write operational logs for each asset

## Notes

This project is best understood as an experimental AI-driven maintenance simulator. The code combines data-driven ML and rule-based decision logic to demonstrate an agentic production-monitoring workflow.

It is a useful starting point for:

- predictive maintenance experiments
- industrial digital twin prototypes
- AI + operations research demos
- teaching fault diagnosis and decision support systems

## Future Directions

Potential extensions include:

- REST API and dashboard UI
- richer optimization/scheduling layer
- more robust model training pipeline
- persistent storage for historical predictions
- deployment to a real manufacturing scenario
