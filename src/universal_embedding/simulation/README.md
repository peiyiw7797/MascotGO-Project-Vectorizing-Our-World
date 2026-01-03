# Simulation Module

**Phase:** 1 — Simulation & Synthetic Data
**Folder:** `src/universal_embedding/simulation/`

This folder contains the **core simulation logic** of the project.
It answers two fundamental questions:

1. **Who are the agents?** (Personas & attributes)
2. **How do they behave over time?** (Interactions & dynamics)

Two Phase 1 issues work **in parallel** inside this folder:

* **Persona & Agent Design**
* **Behavior & Interaction Simulation**

They share the same domain, but **own different files**.

---

## High-level responsibility

This module is responsible for:

* Defining **persona and agent schemas**
* Generating **users and items**
* Simulating **temporal user–item interactions**
* Producing **event logs** used by downstream components

This module **does NOT**:

* Perform feature engineering
* Build multimodal datasets
* Train models
* Evaluate realism (handled elsewhere)

---

## Folder structure & file ownership

```
simulation/
├─ README.md          # (this file)
├─ schemas.py         # persona & agent schemas
├─ population.py     # user/item instantiation
├─ behavior.py       # decision rules
├─ dynamics.py       # temporal dynamics
├─ generator.py      # simulation loop
└─ outputs.py        # standardized outputs
```

### Ownership map

| File            | Owned by                          | Related Issue |
| --------------- | --------------------------------- | ------------- |
| `schemas.py`    | Persona & Agent Design            | Issue #1      |
| `population.py` | Persona & Agent Design            | Issue #1      |
| `behavior.py`   | Behavior Simulation               | Issue #3      |
| `dynamics.py`   | Behavior Simulation               | Issue #3      |
| `generator.py`  | Behavior Simulation (with review) | Issue #3      |
| `outputs.py`    | Shared / integrator               | Both          |

> **Rule:**
> You should only modify files owned by your Issue unless coordinated.

---

## Component overview

### 1. Persona & Agent Design (Issue #1)

**Goal:** Define *what agents are*.

Issue #1 focuses on defining the canonical structure of personas and agents so every downstream component can rely on stable, validated attributes. The workflow should start with schema design and validation rules, then move to parameterizing persona distributions, and finally to generating users/items that conform to those schemas and are reproducible via config + seed.

This work is mostly **static**:

* persona types
* agent attributes
* priors and parameters
* schema validation

**Primary files:**

* `schemas.py` defines what a persona must contain (fields, types, constraints)
* `population.py` instantiates many agents/users/items

**Produces:**

* Structured users and items with persona attributes
  * users.parquet (user-level attributes and persona assignments)
  * items.parquet (item / college representations)
* No temporal behavior yet

**Example:**
* *users.parquet (excerpt)*
  
| user_id | persona   | ability | budget |
| ------- | --------- | ------- | ------ |
| u_001   | ambitious | 0.82    | 0.35   |
| u_002   | cautious  | 0.55    | 0.61   |

* *items.parquet (excerpt)*
  
| item_id | prestige | cost | category |
| ------- | -------- | ---- | -------- |
| i_01    | 0.91     | 0.78 | research |
| i_02    | 0.42     | 0.33 | teaching |

---

### 2. Behavior & Interaction Simulation (Issue #3)

**Goal:** Define *what agents do over time*.

Issue #3 focuses on translating static agents into temporal behavior that can be simulated deterministically. The workflow should begin with specifying action spaces and decision rules, then layering in temporal dynamics and session structure, and finally integrating everything in the simulation loop to emit events that match the required output schema.

This work is **dynamic and stochastic**:

* action selection
* exposure models
* session logic
* time evolution

**Primary files:**

* `behavior.py`
* `dynamics.py`
* `generator.py`

**Produces:**

* `events.parquet`
* `sessions.parquet` - a higher-level temporal structure that groups raw interaction events into realistic user episodes.

**Example:**
* *events.parquet (excerpt)*
  
| event_id | session_id | user_id | item_id | step | event_type | position |
| -------- | ---------- | ------- | ------- | ---- | ---------- | -------- |
| e_0101   | s_0001     | u_001   | i_03    | 120  | view       | 1        |
| e_0102   | s_0001     | u_001   | i_07    | 123  | view       | 2        |
| e_0103   | s_0001     | u_001   | i_07    | 125  | click      | 2        |
| e_0104   | s_0001     | u_001   | i_02    | 130  | view       | 1        |
| e_0105   | s_0001     | u_001   | i_02    | 134  | click      | 1        |

* *sessions.parquet (excerpt)*
  
| session_id | user_id | start_step | end_step | num_events | session_type | device  | entry_source   |
| ---------- | ------- | ---------- | -------- | ---------- | ------------ | ------- | -------------- |
| s_0001     | u_001   | 120        | 134      | 5          | browse       | mobile  | home_feed      |
| s_0002     | u_001   | 980        | 990      | 3          | decision     | desktop | search         |
| s_0003     | u_002   | 450        | 462      | 4          | browse       | mobile  | recommendation |

---

## Interfaces (DO NOT BREAK)

### Inputs

* Persona definitions from `schemas.py`
* Users/items from `population.py`
* Configuration from `configs/*.yaml`

### Outputs

* `events.parquet`
* `sessions.parquet`

Each event **must include**:

* `event_id`
* `session_id`
* `user_id`
* `item_id`
* timestamp or step index
* interaction type (view / click / purchase / etc.)
* relevant context (e.g. position, exposure source)

Downstream code assumes these schemas are **stable**.

---

## How to run locally (Phase 1)

Typical entrypoint (via pipelines):

```bash
python -m universal_embedding.pipelines.run_simulation \
  --config configs/small.yaml
```

Outputs will appear under:

```
data/synthetic/<run_id>/
├─ users.parquet
├─ items.parquet
├─ events.parquet
└─ metadata.json
```

---

## Development rules (please read)

### Configuration

* No hard-coded parameters
* All randomness must be seed-controlled
* Use config files for behavior knobs

### Determinism

* Same config + same seed → same outputs
* This is **mandatory** for Phase 1

### Boundaries

* ❌ Do not do feature engineering here
* ❌ Do not add labels here
* ❌ Do not depend on real external data

If you think something *should* live here but doesn’t, open an Issue.

---

## When modifying shared files

If you need to touch:

* `generator.py`
* `outputs.py`

You must:

* Explain why in the PR
* Request review from the other Issue owner

---

## Mental model (remember this)

> **schemas & population define the world**
> **behavior & dynamics make the world move**

If you keep this separation, this module stays clean and extensible.

---

## Questions?

If unsure:

* Check the related GitHub Issue
* Ask before changing interfaces

This module is the **foundation** of Phase 1 — changes here ripple everywhere.
