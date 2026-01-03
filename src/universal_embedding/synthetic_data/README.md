
# Multimodal Synthetic Data Generation (Issue #2)

**Phase:** 1 — Simulation & Synthetic Data
**Primary folder:** `src/universal_embedding/synthetic_data/`

---

## 1. What this issue is about (TL;DR)

This module turns **synthetic interactions** into **aligned multimodal training data**.

It answers one core question:

> **Given simulated users, items, and events, how do we generate consistent multimodal representations that can be learned by embedding models?**

This issue is the **bridge** between:

* Phase 1 simulation (who exists, what happens)
* Phase 2 embedding learning (how models consume data)

---

## 2. High-level goal

Generate **aligned multimodal synthetic data**—text, image references, tabular features, and metadata—such that:

* All modalities refer to the **same underlying event**
* IDs are **globally consistent**
* Temporal ordering is preserved
* Downstream embedding models can consume the data **without special casing**

---

## 3. What this module does

This module is responsible for:

* Reading synthetic tables from simulation:

  * users
  * items
  * events
  *  sessions
* Generating modality-specific artifacts:

  * text (e.g. descriptions, narratives)
  * image references (paths or placeholders)
  * structured metadata
* Producing **cross-modal aligned samples**
* Ensuring deterministic generation given a fixed seed

---

## 4. What this module does NOT do

This module explicitly does **NOT**:

* ❌ Simulate user behavior
* ❌ Modify personas, agents, or events
* ❌ Train models
* ❌ Evaluate embeddings
* ❌ Perform realism evaluation
* ❌ Create train/val/test splits for modeling

Those concerns belong to **other issues or later phases**.

---

## 5. Folder structure & ownership

```
synthetic_data/
├─ README.md              # this file
├─ dataset_builder.py     # main orchestration logic
├─ feature_engineering.py # modality construction only
├─ labeling.py            # optional, clearly separated
└─ splits.py              # grouping only (no ML splits)
```

> This issue owns **all files in this folder**.

---

## 6. Inputs (DO NOT BREAK)

All inputs are **read-only**.

| Input file                    | Source                     |
| ----------------------------- | -------------------------- |
| `users.parquet`               | `data/synthetic/<run_id>/` |
| `items.parquet`               | `data/synthetic/<run_id>/` |
| `events.parquet`              | `data/synthetic/<run_id>/` |
| `sessions.parquet`            | `data/synthetic/<run_id>/` |

**Assumptions:**

* IDs are stable and globally unique
* Schemas are defined by the simulation module
* Temporal ordering already exists in events

---

## 7. Outputs 

### Primary output
Output location

This module writes all artifacts to `data/multimodal/<run_id>/`, where `<run_id>` matches the upstream synthetic simulation run. Simulation outputs under `data/synthetic/` are treated as immutable inputs and must not be modified.

Example:
```
data/multimodal/<run_id>/
├─ multimodal_samples.parquet
├─ text/
│  └─ samples.jsonl
├─ images/
│  └─ image_index.csv
└─ metadata.json
```

---

## 7. End-to-End Example: One Event → All Modalities

This section shows how **a single simulated event** is transformed into **aligned multimodal outputs**.

The goal is to make it easy to answer:

> “Given *this* event, what exactly gets generated, and where does it live?”

---

### 7.1 The source event (from simulation)

Assume the following row exists in `events.parquet`:

| event_id | user_id | item_id | step | event_type | position | exposure_source |
| -------- | ------- | ------- | ---- | ---------- | -------- | --------------- |
| e_01023  | u_004   | i_012   | 134  | view       | 1        | home_feed       |

**Interpretation (plain English):**

> User `u_004` viewed item `i_012` at time step 134, shown in position 1 on the home feed.

This single row is the **ground truth anchor** for everything below.

---

### 7.2 Multimodal sample record

From this event, the dataset builder creates **one multimodal sample**:

#### `multimodal_samples.parquet`

| sample_id | event_id | user_id | item_id | step | text_ref  | image_ref | tabular_ref |
| --------- | -------- | ------- | ------- | ---- | --------- | --------- | ----------- |
| s_00001   | e_01023  | u_004   | i_012   | 134  | txt_00001 | img_00001 | tab_00001   |

Key rule:

* `sample_id` is the **cross-modal join key**
* All modalities below reference `sample_id = s_00001`

---

### 7.3 Text modality (natural-language view)

#### `text/samples.jsonl`

```json
{
  "text_id": "txt_00001",
  "sample_id": "s_00001",
  "event_id": "e_01023",
  "content": "The student browsed a highly ranked research-focused college that appeared first in their recommendations.",
  "persona_hint": "ambitious",
  "style": "descriptive",
  "language": "en"
}
```

What this represents:

* A **textual rendering** of the event
* Deterministic, template-driven
* Grounded in:

  * event type (`view`)
  * item attributes (prestige, category)
  * context (`position = 1`, `home_feed`)

---

### 7.4 Image modality (visual reference)

#### `images/image_index.csv`

| image_id  | sample_id | item_id | image_type         | path                  |
| --------- | --------- | ------- | ------------------ | --------------------- |
| img_00001 | s_00001   | i_012   | campus_placeholder | images/campus_012.png |

What this represents:

* A **visual stand-in** for the item being viewed
* No requirement for real image generation in Phase 1
* Used to test multimodal alignment and pipelines

---

### 7.5 Tabular modality (structured view)

#### `tabular_features.parquet`

| tabular_id | sample_id | user_budget | item_cost | item_prestige | exposure_position |
| ---------- | --------- | ----------- | --------- | ------------- | ----------------- |
| tab_00001  | s_00001   | 0.35        | 0.78      | 0.91          | 1                 |

What this represents:

* Structured, numeric representation of the same event
* Directly derived from:

  * `users.parquet`
  * `items.parquet`
  * event context

Important:

* These are **modal representations**, not final ML features
* Feature transformations happen in Phase 2

---

### 7.6 Session-aware view

Given `sessions.parquet` and this event belongs to a session:

#### `sessions.parquet`

| session_id | user_id | start_step | end_step |
| ---------- | ------- | ---------- | -------- |
| s_0012     | u_004   | 130        | 142      |

#### Session linkage (implicit or explicit)

| sample_id | session_id | within_session_rank |
| --------- | ---------- | ------------------- |
| s_00001   | s_0012     | 2                   |

---

### 7.7 Invariant alignment rules 

For **every event → sample → modality mapping**, the following must hold:

* [ ] `event_id` exists in `events.parquet`
* [ ] `sample_id` uniquely maps to exactly one event
* [ ] All modalities reference the same `sample_id`
* [ ] `user_id` and `item_id` are consistent everywhere
* [ ] Re-running with the same seed reproduces identical artifacts

If any invariant breaks, **multimodal learning becomes undefined**.



---

## 8. Determinism requirements

This module **must be deterministic**.

> Same inputs + same config + same seed → identical multimodal outputs

Rules:

* All randomness must be seed-controlled
* No implicit randomness in text or image generation
* No dependence on wall-clock time

---

## 9. Dependency boundaries

### Upstream dependencies

* Simulation outputs (Issues #1 and #3)
* Configuration files (`configs/*.yaml`)

### Downstream consumers

* Phase 2 embedding training pipelines
* `evaluation.distribution`

Downstream code **assumes this module is stable**.

---

## 10. Definition of Done (DoD)

This issue is complete when:

* [ ] Multimodal schemas are clearly defined and documented
* [ ] Cross-modal alignment is verified (IDs, timestamps)
* [ ] A small config run produces **all modalities successfully**
* [ ] Deterministic generation is confirmed
* [ ] No simulation logic is duplicated here
* [ ] PR merged with review

---

## 11. Mental model (important)

> **Simulation tells us what happened.
> Multimodal generation tells us how that event is observed across modalities.**

If you feel tempted to:

* change behavior logic
* add new events
* “fix” distributions

You are probably in the **wrong module**.

---

## 12. How to work safely in this issue

* Treat simulation outputs as immutable
* Prefer additive changes over refactors
* Document schemas before changing them
* Keep PRs small and reviewable
* Ask before introducing new modalities
