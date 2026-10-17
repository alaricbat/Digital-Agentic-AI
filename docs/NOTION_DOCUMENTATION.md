# Digital Agentic AI — Project Documentation

> **Purpose:** Notion-ready product, architecture, and delivery documentation for the Digital Agentic AI project. Copy this page into Notion and split the sections into child pages or databases as the project grows.
>
> **Project stage:** Experimental prototype. The current implementation is a predictive-maintenance simulator, not a production industrial control system.

## 1. Executive summary

Digital Agentic AI explores how machine telemetry, predictive models, maintenance rules, and agent-assisted workflows can support industrial operations. The prototype simulates equipment aging and five failure modes using the AI4I 2020 dataset, scores equipment with existing ML artifacts, applies rule-driven parameter adjustments, and writes operating history and diagnostic logs.

The next product direction is an **industrial operations intelligence platform** that can:

- Monitor machine health and production operations in near real time.
- Detect anomalies and predict failure risk with measurable confidence.
- Explain alerts using telemetry, model evidence, and approved maintenance knowledge.
- Recommend safe maintenance or scheduling actions for a human operator.
- Optimize maintenance and production decisions using constrained optimization and, later, offline reinforcement learning.
- Record decisions, approvals, outcomes, and model versions for audit and continuous improvement.

### Product north star

Help operations teams identify emerging equipment risk earlier, understand why it matters, and choose a safe, measurable next action—without allowing an unvalidated AI model to control physical equipment.

## 2. Current state: implemented baseline

| Area | Current implementation |
|---|---|
| Data | AI4I 2020 data in `data/raw/`; simulated per-asset operating history in `data/operating/`. |
| Simulation | A threaded lifecycle per production asset updates speed, temperature, torque, and tool wear and evaluates TWF, HDF, PWF, OSF, and RNF conditions. |
| Predictive models | A saved LightGBM model estimates machine-failure probability. A custom softmax regression model predicts NORMAL, WARNING, or CRITICAL from operating-history features. |
| Decision logic | `KnowledgeAgent` applies product-type thresholds; `PlanningAgent` turns resulting rules into parameter adjustments and a human-readable log. |
| Optimization | Mathematical and scheduling modules exist, but are not wired into the main simulation workflow. |
| Operations visibility | Text logs are written under `src/simulation/logs/`; per-asset CSV histories are written under `data/operating/`. No live dashboard, alert delivery, metrics service, or model-monitoring service is implemented. |
| LLM | There is no LLM inference, prompt workflow, retrieval system, or tool-calling integration in the current agent classes. The “agent” layer is rule-based Python logic. |
| Deep learning | No deep neural network is currently used. LightGBM and custom softmax regression are the implemented models. |
| Reinforcement learning | No RL policy or training loop is currently implemented. |
| Runtime | `main.py` loads the first five AI4I rows and starts asset lifecycle threads. |

Treat this table as the source of truth for current capabilities; planned capabilities below are not yet implemented.

## 3. Product scope and users

### Primary users

- **Maintenance technician:** Needs a clear alert, likely failure mode, and practical inspection steps.
- **Reliability engineer:** Needs trends, model performance, failure analysis, and fleet-level comparisons.
- **Operations supervisor:** Needs equipment status, production impact, and recommended schedule changes.
- **ML/AI engineer:** Needs reproducible datasets, model versions, evaluation results, and drift signals.
- **Plant administrator:** Needs asset configuration, user access, alert routing, and audit history.

### Initial use cases

1. View the live and historical health of registered assets.
2. Detect abnormal sensor behavior and identify a likely failure mode.
3. Estimate failure probability and a useful prediction horizon.
4. Explain an alert with evidence and uncertainty.
5. Recommend an inspection, maintenance work order, or schedule change.
6. Capture operator feedback and compare the recommendation with the eventual outcome.

### Out of scope for the initial release

- Autonomous commands to physical equipment.
- Unreviewed online reinforcement-learning updates.
- Claims of industrial-grade reliability based only on synthetic simulation or AI4I benchmark performance.
- Replacing a safety instrumented system, PLC interlock, or qualified maintenance procedure.

## 4. Architecture overview

### Current data and decision flow

```text
AI4I CSV
   ↓
main.py → ProductionAsset → Lifecycle thread
                              ├─ LightGBM failure score
                              ├─ Softmax operating-state prediction
                              ├─ KnowledgeAgent threshold checks
                              ├─ PlanningAgent parameter adjustments
                              ├─ failure-mode lifecycle checks
                              └─ CSV history + text diagnostic log
```

### Target architecture (phased)

```text
Sensors / simulator / files
          ↓
Ingestion API → validation, timestamps, asset identity, unit normalization
          ↓
Time-series store + event/audit store
          ↓
Feature pipeline → anomaly detection → failure prediction
          ↓
Policy and safety layer ← approved maintenance knowledge (RAG)
          ↓
Recommendation API → dashboard / alert channel → operator approval
          ↓
Outcome and feedback capture → evaluation, retraining, model registry
```

Keep ingestion, inference, recommendations, and operator approval as distinct boundaries. A model prediction is evidence for a recommendation; it is not authorization to actuate equipment.

### Target service boundaries

| Component | Responsibility |
|---|---|
| Telemetry ingestion | Accept simulator or sensor events; validate schema, units, timestamps, and asset IDs. |
| Asset and configuration service | Store equipment metadata, operating limits, and versioned configuration. |
| Feature and inference service | Apply a versioned feature pipeline and produce calibrated, timestamped predictions. |
| Decision service | Combine model evidence, deterministic safety rules, and approved operating procedures. |
| Knowledge service | Retrieve cited, versioned maintenance documents for operator-facing explanations. |
| Operations API and UI | Show asset health, alerts, trends, recommendations, and operator actions. |
| Monitoring and audit | Track service health, data quality, predictions, decisions, approvals, and outcomes. |
| Training and evaluation pipeline | Build reproducible datasets, compare candidate models, and register approved versions. |

## 5. Data and domain glossary

### Failure modes in the prototype

| Code | Meaning in project | Current simulated signal |
|---|---|---|
| TWF | Tool Wear Failure | Tool wear threshold and wear accumulation. |
| HDF | Heat Dissipation Failure | Process-to-air temperature difference and rotational speed. |
| PWF | Power Failure | Estimated mechanical power from torque and rotational speed. |
| OSF | Over-Strain Failure | Tool-wear load multiplied by torque, compared with type-specific limits. |
| RNF | Random Failure | Seeded random event and a simulated instability score. |

### Main telemetry fields

| Field | Meaning | Notes |
|---|---|---|
| UDI | Dataset row identifier | Source-data identity; not necessarily a production asset ID. |
| Product ID | Dataset product/machine identifier | Used to identify a simulated asset and its output files. |
| Type | L, M, or H product type | Drives selected simulation and rule thresholds. |
| Air temperature [K] | Ambient temperature | Kelvin in the source dataset. |
| Process temperature [K] | Process temperature | Kelvin in the source dataset. |
| Rotational speed [rpm] | Spindle speed | Revolutions per minute. |
| Torque [Nm] | Torque | Newton-metres. |
| Tool wear [min] | Accumulated tool wear | Source field name indicates minutes; simulation increments it per tick. |
| Machine failure | Dataset failure label | Binary source target; distinguish labels from live inference in future schemas. |
| TWF, HDF, PWF, OSF, RNF | Failure-mode indicators | Binary labels/flags in the source and simulator. |
| Operation State | Simulator state | NORMAL, WARNING, or CRITICAL. |

**Data contract to establish:** Add a canonical event schema with `asset_id`, `event_time` (UTC), `ingested_at`, sensor values with explicit units, quality flags, source, and schema version. Keep ground-truth failure labels separate from predictions and operator-assigned status.

## 6. Existing repository map

| Path | Role |
|---|---|
| `main.py` | Loads a small dataset subset and starts asset simulations. |
| `src/agent_llm/` | Rule-based knowledge, planning, and action classes; despite the folder name, these are not LLM integrations. |
| `src/simulation/entities/` | Product types and production-asset construction. |
| `src/simulation/lifecyle/` | Threaded lifecycle, simulated degradation, failure checks, prediction calls, and CSV recording. |
| `src/simulation/ml/` | AI module interface. |
| `src/simulation/state/` | Operation-state and failure-mode definitions. |
| `src/ml_dl/clazz/` | Custom softmax regression implementation. |
| `src/ml_dl/model/` | Serialized LightGBM and softmax model artifacts. |
| `src/ml_dl/*.ipynb` | Model exploration, training, evaluation, and artifact export notebooks. |
| `src/optimization/` | Mathematical optimization and scheduling code, not currently connected to the main path. |
| `src/utils/Writer.py` | Text-file logging helper. |
| `data/raw/` | Source datasets, including AI4I 2020. |
| `data/operating/` | Per-asset simulation CSV output. |
| `src/simulation/logs/` | Per-asset diagnostic text output. |

## 7. Product requirements and success measures

### Functional requirements

- Asset list with state, last-seen time, current risk, and alert count.
- Asset detail with sensor trends, predicted failure modes, model evidence, and event history.
- Configurable warning and critical thresholds with version history and access controls.
- Alerts that are deduplicated, acknowledged, assigned, escalated, and resolved.
- Recommendations that include rationale, confidence/uncertainty, evidence timestamps, and required human approval.
- Feedback capture: accepted, rejected, modified, completed, false alarm, and confirmed failure.
- Searchable audit records linking input data, model version, policy version, recommendation, and human decision.

### Initial quality targets (proposed; confirm against real operational needs)

| Measure | Initial target |
|---|---|
| Telemetry completeness | At least 99% of expected events available over a rolling 24-hour window in the pilot. |
| Alert delivery latency | P95 under 60 seconds from accepted event to dashboard alert in the pilot. |
| Service availability | At least 99.5% monthly availability for the pilot dashboard/API, excluding planned maintenance. |
| Alert usefulness | Track precision, recall, false-alert rate, and lead time by asset and failure mode; establish a baseline before setting a release gate. |
| Auditability | 100% of recommendations link to the relevant input window, model version, policy version, and operator outcome. |
| Safety | 0 autonomous physical control actions in initial releases. |

These are planning targets, not measured results or current guarantees.

## 8. Technical upgrade strategy

### 8.1 Foundation: correctness and reliability

Do this before adding more sophisticated models:

- Add automated tests for feature construction, model input shapes, thresholds, lifecycle transitions, and failure-state precedence.
- Validate that model artifacts exist, load without mutation, and match the expected feature schema and version.
- Define a single feature pipeline shared by training and inference; persist scaling parameters instead of deriving them from each live history window.
- Make each simulation run reproducible and configurable: seed, asset count, tick interval, data source, and output location.
- Add graceful thread shutdown and clear error reporting for per-asset inference failures.
- Separate event data, model predictions, rule decisions, and physical state changes in records.
- Add structured logging and explicit configuration rather than relying on hard-coded paths and thresholds.

**Release gate:** deterministic tests pass; model features match between training and inference; invalid or missing input cannot silently become a healthy prediction.

### 8.2 ML and deep-learning roadmap

1. **Baseline evaluation:** Establish time-aware and asset-aware train/validation/test splits. Report per-failure-mode precision, recall, PR-AUC, calibration, confusion matrices, false alarms per asset-day, and warning lead time.
2. **Class imbalance and calibration:** Compare class-weighted baselines, threshold selection by operational cost, and probability calibration. Do not choose thresholds from accuracy alone.
3. **Time-series features:** Add rolling statistics, rates of change, lagged features, missingness, and operating context using a consistent online/offline pipeline.
4. **Anomaly detection:** Evaluate a transparent statistical baseline first; compare isolation-based or reconstruction-based approaches only where they address a measured gap.
5. **Deep learning (optional, evidence-driven):** Evaluate temporal convolutional networks, LSTM/GRU, or transformer time-series models only when enough correctly timestamped sequence data is available. Compare with LightGBM on the same split and operational metrics.
6. **Model registry and deployment:** Record artifact, feature schema, training-data version, code revision, evaluation report, owner, and approval status for every model version.
7. **Shadow deployment:** Run candidate models beside the incumbent without affecting recommendations; compare predictions and latency before approval.

**Model acceptance checklist**

- [ ] Dataset lineage and label definition documented.
- [ ] Leakage review and time/asset split completed.
- [ ] Per-failure-mode metrics and calibration reviewed.
- [ ] Thresholds selected against explicit operational cost.
- [ ] Inference latency, missing data, and out-of-distribution behavior tested.
- [ ] Rollback path and model owner recorded.

### 8.3 LLM and retrieval-augmented generation (RAG)

Use an LLM for language and knowledge tasks—not as a replacement for deterministic limits or validated failure predictors.

**Good initial LLM use cases**

- Summarize an existing alert in operator-friendly language.
- Explain which telemetry values and rules contributed to a recommendation.
- Retrieve approved SOPs and maintenance documents and cite the exact source.
- Convert an operator question into a read-only asset/history query.
- Draft a maintenance work order for human review.
- Summarize a shift or recurring issue from audited events.

**Recommended request flow**

1. Receive an operator question or a structured alert.
2. Resolve the user's access and the asset scope.
3. Fetch authorized telemetry, prediction, and rule-decision records from application services.
4. Retrieve only approved, versioned maintenance content; attach source identifiers and passages.
5. Ask the LLM for a structured response: summary, evidence, citations, uncertainty, and suggested next step.
6. Validate the output schema and citations; reject unsupported or malformed claims.
7. Present the response for human review and record feedback.

**LLM guardrails**

- Never let generated text change thresholds, write to a PLC, or issue a physical control command.
- Start with read-only, allowlisted tools. Require authorization and confirmation for any state-changing workflow.
- Keep system instructions and retrieved documents separate; treat retrieved content and user input as untrusted data.
- Require citations for procedural claims; show “insufficient evidence” when retrieval is weak.
- Minimize sensitive data sent to model providers; document retention, region, and privacy settings before production use.
- Log model/provider/version, prompt-template version, retrieved source IDs, tool calls, validation results, and user feedback without unnecessarily storing secrets.
- Evaluate factuality, citation correctness, refusal behavior, latency, and cost on a versioned test set.

**Not in the first LLM release:** autonomous diagnosis that bypasses model/rule evidence, open-ended command execution, or direct machine control.

### 8.4 Reinforcement learning and operations optimization

Treat RL as a research phase, after a validated simulator, explicit action constraints, and a reliable offline evaluation harness exist. The current simulator is not yet sufficient evidence of safe real-world policy behavior.

**Suggested progression**

1. Use deterministic optimization or scheduling baselines for maintenance windows and job sequencing.
2. Formalize a decision problem in simulation:
   - **Observation:** recent telemetry, asset state, uncertainty, production context, maintenance status.
   - **Actions:** initially advisory choices such as inspect, schedule maintenance, defer within policy, or request human review—not actuator commands.
   - **Reward/cost:** downtime, maintenance cost, production impact, false alarms, and safety violations with explicit weighting.
   - **Constraints:** approved operating envelope, hard safety rules, action availability, and required human approval.
3. Build scenario coverage for normal operation, each known failure mode, sensor dropouts, distribution shift, and rare events.
4. Compare an RL candidate with a rule-based and mathematical-optimization baseline using identical scenarios and seeds.
5. Use offline evaluation and shadow recommendations; require engineering and operations approval before any pilot.
6. Keep the safety shield and emergency stop independent of the learned policy. Never use unconstrained online exploration on production equipment.

**RL release gate:** demonstrate robust improvement over baselines across held-out scenarios, no hard-constraint violations in the test suite, explainable action records, human approval, and a tested fallback policy.

## 9. Operations monitoring and observability

### Dashboard pages

1. **Fleet overview:** online/offline assets, NORMAL/WARNING/CRITICAL counts, highest-risk assets, unacknowledged alerts, and ingestion freshness.
2. **Asset detail:** current readings, trends, prediction history, thresholds, failure-mode evidence, alert timeline, and maintenance history.
3. **Alerts and work:** severity, asset, probable mode, age, owner, acknowledgement, recommendation, and resolution outcome.
4. **Model health:** version, traffic, latency, error rate, prediction distribution, calibration/quality when labels arrive, and drift indicators.
5. **Data health:** event volume, missing/late/duplicate readings, schema failures, unit/range violations, and sensor freshness.
6. **Audit and configuration:** threshold edits, model promotions, approvals, access events, and recommendation outcomes.

### What to monitor

| Signal | Example measurements |
|---|---|
| Service health | API availability, request rate, errors, queue depth, worker status. |
| Telemetry health | Events received, lag, missing fields, duplicates, invalid ranges, clock skew. |
| Inference health | Requests, latency percentiles, failures, model load/version, fallback count. |
| Prediction behavior | Score distribution, alert rate, predicted classes, confidence/uncertainty, drift. |
| Operational outcomes | Acknowledgement time, time-to-resolution, confirmed failure, false alert, maintenance completion. |
| Resource/cost | CPU, memory, storage growth, model/provider tokens and cost if an LLM is added. |

### Alert routing

- **Critical:** immediate operator notification and escalation according to plant policy; recommendation remains advisory.
- **Warning:** display in the operations queue with acknowledgement and follow-up workflow.
- **Informational:** retain in history and surface in trends; do not page operators.
- Deduplicate repeated events by asset, failure mode, and time window; preserve each underlying event for audit.
- Track delivery, acknowledgement, assignment, escalation, and resolution separately.

### Suggested observability stack (decision pending)

Begin with structured application logs, health endpoints, and persistent operational records. Evaluate Prometheus-compatible metrics and Grafana dashboards for a self-hosted path, or a managed observability platform if deployment constraints favor it. Choose a time-series database only after ingestion volume, retention, and hosting requirements are known.

## 10. Security, privacy, and safety

- Authenticate users and services; apply role-based access to assets, configuration, and maintenance records.
- Use TLS in transit and managed encryption at rest for deployed environments.
- Keep credentials outside source code and logs; use a secret manager in deployment.
- Maintain audit logs for model promotion, threshold changes, access, recommendations, and approvals.
- Define data ownership, retention, deletion, backup, and export requirements before connecting real plant data.
- Validate sensor identity, timestamps, ranges, units, and payload sizes at ingestion.
- Apply least privilege to integrations and isolate read-only monitoring from control networks.
- Treat every AI recommendation as advisory until formally validated and approved for its intended use.
- Document hazard analysis, operating envelopes, fallback behavior, and escalation responsibility with qualified domain experts.

## 11. Delivery roadmap

| Phase | Focus | Deliverables | Exit criteria |
|---|---|---|---|
| 0. Stabilize prototype | Reproducibility, tests, schemas, startup/shutdown, artifact handling | Configurable simulator, test suite, canonical event/prediction schema, known-issue list | Repeatable runs; tests cover core features and state transitions; no silent model fallback. |
| 1. Operational visibility | Persistent records, API, fleet/asset views, alerts, audit | Read-only monitoring dashboard and operator alert lifecycle | Data freshness and alert lifecycle visible; audit links each recommendation to evidence. |
| 2. Model quality | Evaluation pipeline, calibration, model registry, drift monitoring | Baseline report, repeatable training/evaluation, shadow deployment | Candidate model meets agreed operational metrics and rollback is proven. |
| 3. LLM assistant | Curated SOP knowledge base, cited summaries, read-only tools | Operator Q&A and work-order drafts with review | Citation and safety evaluations pass; no unapproved write/control tools. |
| 4. Optimization/RL research | Scheduling baseline, constrained simulator, offline evaluation | Comparable policies, scenario suite, safety shield design | Candidate beats baseline across held-out scenarios without constraint violations. |
| 5. Controlled pilot | Deployment hardening, access, on-call, operational validation | Limited read-only/advisory pilot with trained users | Operations, reliability, safety, and security owners approve expansion. |

### Prioritized first backlog

- [ ] **P0:** Add tests for inference features, normalization, threshold decisions, and NORMAL/WARNING/CRITICAL aggregation.
- [ ] **P0:** Persist and reuse the training scaler; ensure inference uses the same feature order and transformation as training.
- [ ] **P0:** Make model loading read-only and validate artifact schema/version at startup.
- [ ] **P0:** Add explicit behavior and an observable error state for missing/corrupt model artifacts and missing operating history.
- [ ] **P0:** Add a simulation configuration and graceful shutdown; make random seeds configurable.
- [ ] **P1:** Define and validate a versioned telemetry/event schema with units and UTC timestamps.
- [ ] **P1:** Separate structured event/prediction/action records from display-oriented log messages.
- [ ] **P1:** Build a read-only fleet and asset health API/dashboard.
- [ ] **P1:** Implement alert acknowledgement, assignment, escalation, and resolution tracking.
- [ ] **P2:** Produce per-failure-mode offline model evaluation and shadow comparison.
- [ ] **P2:** Add model/data drift and prediction-service health monitoring.
- [ ] **P3:** Prototype cited RAG summaries using approved maintenance documents.
- [ ] **P4:** Evaluate maintenance scheduling optimization before RL.

## 12. Risks and open decisions

| Risk / question | Why it matters | Proposed next step |
|---|---|---|
| Benchmark-to-plant gap | AI4I and simulated data may not represent real sensors, failure rates, or maintenance processes. | Identify a representative pilot dataset and domain reviewer before making performance claims. |
| Label imbalance and leakage | Rare failures and random train/test splits can overstate performance. | Use time- and asset-aware splits; report per-mode precision/recall, PR-AUC, calibration, and lead time. |
| Current inference consistency | Notebook training and runtime feature/scaling paths must be verified as identical. | Create a shared preprocessing artifact and parity tests before relying on predictions. |
| Simulation fidelity | Simplified degradation and stochastic events may not model plant dynamics. | Validate assumptions with reliability/controls engineers; record simulator limitations. |
| Safety responsibility | Incorrect recommendations could affect people, equipment, and production. | Keep human approval and independent safety interlocks; complete hazard review before deployment. |
| LLM hallucinations and prompt injection | Retrieved or user-provided text may be incorrect or malicious. | Use approved-source retrieval, citations, schema validation, least-privilege tools, and red-team tests. |
| RL reward loopholes | A policy can optimize a proxy while violating operational intent. | Begin advisory-only; test hard constraints and held-out adversarial scenarios. |
| Infrastructure choices | Hosting, sensor protocols, data volumes, and retention are not yet specified. | Decide pilot constraints before selecting database, queue, cloud, or dashboard stack. |
| Model threshold policy | Current thresholds are hard-coded and may differ across data, simulation, and operational needs. | Version thresholds and have domain owners approve changes. |

## 13. Governance and ownership

Assign a named owner before each production-facing capability is enabled.

| Responsibility | Suggested owner |
|---|---|
| Product scope and operator workflow | Product owner / operations lead |
| Failure definitions and maintenance procedures | Reliability engineer |
| Sensor integration and unit correctness | Controls / data engineer |
| Training, evaluation, and model promotion | ML engineer |
| Identity, deployment, and incident response | Platform / security owner |
| Safety review and approval | Qualified plant safety and engineering representatives |

Every model, threshold, prompt template, retrieval corpus, and decision policy should have a version, owner, change record, evaluation, and rollback path.

## 14. Notion workspace structure

Suggested top-level Notion pages:

1. **Digital Agentic AI — Home** (executive summary, status, owners, links)
2. **Product Requirements** (users, use cases, requirements, success metrics)
3. **Architecture & Data Contracts** (diagrams, services, schemas, integrations)
4. **ML Model Catalog** (model card per version, datasets, metrics, deployment status)
5. **Operations Monitoring** (dashboards, alerts, runbooks, incidents)
6. **LLM Assistant & Knowledge Base** (approved sources, evaluations, guardrails)
7. **Optimization & RL Research** (environment, action constraints, reward, scenarios)
8. **Roadmap & Backlog** (prioritized work, owner, status, dependency, acceptance criteria)
9. **Risks, Decisions & Incidents** (decision records, risk register, incident review)

### Suggested Notion databases

**Assets**

`Asset ID` · `Name` · `Type` · `Site` · `Status` · `Last Seen` · `Current Risk` · `Owner` · `Configuration Version`

**Alerts**

`Alert ID` · `Asset` · `Severity` · `Failure Mode` · `Created At` · `Acknowledged By` · `Status` · `Recommendation` · `Resolution` · `Model Version`

**Models**

`Model Name` · `Version` · `Task` · `Training Data` · `Feature Schema` · `Metrics` · `Status` · `Owner` · `Approved At` · `Rollback Version`

**Decisions**

`Decision ID` · `Asset` · `Input Window` · `Prediction` · `Rule/Policy Version` · `Recommendation` · `Human Decision` · `Outcome` · `Created At`

**Roadmap**

`Task` · `Priority` · `Phase` · `Owner` · `Status` · `Acceptance Criteria` · `Dependencies` · `Target Date`

## 15. Glossary

- **Agent:** In the current code, a Python component that applies deterministic diagnostic or planning logic. It does not currently call an LLM.
- **Digital twin/simulator:** A software representation of asset state and lifecycle; this prototype uses simplified simulated dynamics.
- **Failure probability:** A model score that requires calibration and an operational threshold before being interpreted as a probability for decision-making.
- **RAG:** Retrieval-augmented generation; an LLM response grounded in retrieved, approved reference documents.
- **Shadow deployment:** Running a candidate model alongside the active model without letting candidate output drive operational recommendations.
- **Drift:** A change in telemetry or prediction distributions that may indicate altered equipment, sensors, or operating conditions.
- **Safety shield:** An independent set of constraints that blocks disallowed actions, regardless of a learned policy's recommendation.
- **Offline RL evaluation:** Evaluating a learned policy from logged/simulated data without exploratory actions on live equipment.

## 16. References in this repository

- Project overview: [README.md](../README.md)
- Runtime entry point: [main.py](../main.py)
- Lifecycle and simulation: [Lifecycle.py](../src/simulation/lifecyle/Lifecycle.py)
- Rule-based diagnosis: [KnowledgeAgent.py](../src/agent_llm/KnowledgeAgent.py)
- Planning behavior: [PlanningAgent.py](../src/agent_llm/PlanningAgent.py)
- Action labels: [ActionAgent.py](../src/agent_llm/ActionAgent.py)
- LightGBM training notebook: [LightBGM.ipynb](../src/ml_dl/LightBGM.ipynb)
- Softmax training notebook: [SoftmaxRegression.ipynb](../src/ml_dl/SoftmaxRegression.ipynb)
- Scheduler module: [scheduler.py](../src/optimization/scheduler.py)
