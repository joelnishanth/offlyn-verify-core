# Prototype

Software simulation of the Offlyn Verify Core actuation-boundary enforcement architecture.

## Quick Start

```bash
cd prototype
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Tests

```bash
pytest -v
```

## Run Scenarios

```bash
python -m planner.scenarios --scenario safe_move
python -m planner.scenarios --scenario speed_violation
python -m planner.scenarios --scenario replay_attack
python -m planner.scenarios --scenario direct_actuator_bypass
python -m planner.scenarios --scenario all
```

## Docker

```bash
docker compose up --build
```

## Structure

```
planner/        AI planner simulator and scenario runner
policy/         Policy compiler, signer, verifier, and YAML policies
gate/           Verify Core gate, decision engine, audit log, schemas
actuator_sim/   Robot arm and drone actuator simulators
tests/          Pytest test suite
```
