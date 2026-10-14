# Digital Agentic AI

Digital Agentic AI is a Python-based predictive maintenance simulator that combines a machine lifecycle model, AI-based fault scoring, and rule-driven operational decisions for industrial equipment monitoring.

The project uses the AI4I 2020 Predictive Maintenance dataset to model equipment behavior under normal operation and multiple simulated failure modes:

- TWF: Tool Wear Failure
- HDF: Heat Dissipation Failure
- PWF: Power Failure
- OSF: Over-Stress Failure
- RNF: Random Failure

It also includes a lightweight agent layer that evaluates operating conditions, applies corrective actions, and writes human-readable maintenance logs.

## Project goals

This repository demonstrates an "agentic" workflow for manufacturing intelligence, including:

- simulating production assets over a lifecycle
- interpreting sensor values and process conditions
- loading ML model artifacts for anomaly/failure prediction
- applying operational rule checks for risk mitigation
- recording diagnostics and maintenance actions in log files

## Repository structure

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
│   ├── ml_dl/
│   │   ├── clazz/
│   │   ├── model/
│   │   ├── LightBGM.ipynb
│   │   └── SoftmaxRegression.ipynb
│   ├── optimization/
│   │   ├── mathematical.py
│   │   └── scheduler.py
│   ├── simulation/
│   │   ├── entities/
│   │   ├── lifecyle/
│   │   ├── logs/
│   │   ├── ml/
│   │   └── state/
│   └── utils/
│       └── Writer.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt (if added later)
```

## Data and modeling

The system reads operating data from `data/raw/ai4i2020.csv` and builds simulated `ProductionAsset` objects from the row values, including:

- air temperature
- process temperature
- rotational speed
- torque
- tool wear
- machine failure flag
- failure mode indicators

The project loads model artifacts from `src/ml_dl/model/` and combines them with threshold-based decision rules in the agent layer.

## Prerequisites

- Python 3.10+
- pip

Install the dependencies:

```bash
pip install pandas numpy lightgbm
```

## Quick start

From the repository root, run:

```bash
python3 main.py
```

This entry point loads a subset of the dataset, creates `ProductionAsset` instances, and runs the lifecycle simulation. The simulator emits AI integration messages and maintenance diagnostics while processing the assets.

## Example runtime flow

1. Load equipment data from the raw dataset
2. Instantiate production assets
3. Initialize ML model components
4. Evaluate risk and operating parameters
5. Trigger corrective actions when thresholds are exceeded
6. Save operational logs under `src/simulation/logs/`

## Notes

This project is intended as an experimental industrial AI and digital-twin prototype. It blends:

- data-driven ML signals
- rule-based maintenance logic
- agent-style decision planning
- operational simulation of equipment aging and failure events

Potential use cases include:

- predictive maintenance experiments
- industrial monitoring demos
- AI + operations decision systems
- teaching fault diagnosis and maintenance planning

## Future directions

Possible enhancements include:

- a REST API or dashboard interface
- richer optimization and scheduling modules
- expanded model training pipelines
- persistent historical analytics storage
- deployment into more realistic manufacturing scenarios
