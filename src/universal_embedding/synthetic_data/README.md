# Multimodal Synthetic Data Generation (Issue #2)

**Phase:** 1 — Simulation & Synthetic Data
**Primary folder:** `src/universal_embedding/synthetic_data/`

---

## 1. What this issue is about (TL;DR)

This module turns **synthetic interactions and personas** into **aligned multimodal profiles** suitable for downstream embedding learning.

It answers one core question:

> **Given simulated users, items, events, and sessions, how do we generate rich, consistent multimodal representations that embedding models can learn from?**

This issue is the **bridge** between:

* **Phase 1 simulation** — who exists, what happens
* **Phase 2 embedding learning** — how models consume multimodal data

---

## 2. High-level goal

Generate **complete multimodal synthetic profiles**—text, image references, audio/text surrogates, structured metadata, and relational context—such that:

* All modalities are **grounded in the same underlying events**
* IDs are **globally consistent**
* Temporal ordering is preserved
* LLM-generated content is **schema-constrained and reproducible**
* Downstream embedding models can consume data **without special casing**

This module operationalizes the vision of:

> *“LLM-powered agents creating complete multimodal profiles”*

— while keeping behavior simulation deterministic and scalable.

---

## 3. What this module does

This module is responsible for:

### 3.1 Reading simulation outputs (read-only)

From `data/synthetic/<run_id>/`:

* `users.parquet`
* `items.parquet`
* `events.parquet`
* `sessions.parquet`

These tables define **ground truth structure**:

* who the user is
* what item exists
* what interaction occurred
* when and in what session context

---

### 3.2 Generating modality-specific artifacts (LLM + programmatic)

From those anchors, this module generates **multimodal views of the same underlying reality**, including:

#### Expressive / semantic modalities (LLM-powered, offline)

* Interests and self-descriptions
* Journal entries
* Poetry or creative writing
* Voice-note *transcripts* (text form)
* Descriptive captions for photos
* Persona-consistent narratives of interactions

#### Structural / behavioral modalities (programmatic)

* Clickstream-aligned samples
* Session-aware context
* Tabular attributes derived from users/items/events
* Peer or cohort references (IDs only, no graph learning)

LLMs are used **only as generators**, never as live agents.

---

### 3.3 Producing cross-modal aligned samples

For each eligible event (or session):

* Create a `sample_id`
* Attach one or more modality artifacts
* Ensure all modalities reference the same:

  * `sample_id`
  * `event_id`
  * `user_id`
  * `item_id`
  * timestamp / step

The result is a **joinable, modality-agnostic dataset**.

---

### 3.4 Ensuring determinism

Even when LLMs are used:

* All generation is:

  * schema-constrained
  * seed-controlled
  * cached
* Re-running with the same inputs, config, and seed produces **identical outputs**

---

## 4. What this module does NOT do

This module explicitly does **NOT**:

* ❌ Simulate user behavior
* ❌ Modify personas, agents, or events
* ❌ Create or alter clickstream logic
* ❌ Train or evaluate models
* ❌ Perform realism evaluation
* ❌ Create ML train/val/test splits

> **Simulation decides what happened.
> This module decides how that event is observed across modalities.**

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

This issue owns **all files in this folder**.

---

## 6. Inputs (DO NOT BREAK)

All inputs are **read-only**.

| Input file         | Source                     |
| ------------------ | -------------------------- |
| `users.parquet`    | `data/synthetic/<run_id>/` |
| `items.parquet`    | `data/synthetic/<run_id>/` |
| `events.parquet`   | `data/synthetic/<run_id>/` |
| `sessions.parquet` | `data/synthetic/<run_id>/` |

**Assumptions**

* IDs are stable and globally unique
* Schemas are defined by the simulation module
* Temporal ordering already exists
* `sessions.parquet` aligns to `events.parquet` via `session_id`

---

## 7. Outputs

### 7.1 Output location

All outputs are written to:

```
data/multimodal/<run_id>/
```

Simulation outputs under `data/synthetic/` are treated as **immutable inputs**.

---

### 7.2 Primary outputs

Example structure:

```
data/multimodal/<run_id>/
├─ multimodal_samples.parquet
├─ text/
│  └─ samples.jsonl
├─ images/
│  └─ image_index.csv
├─ audio/
│  └─ voice_note_index.csv
├─ tabular_features.parquet
└─ metadata.json
```

---

## 8. End-to-End Example: One Event → Complete Multimodal Profile

### 8.1 Source event (simulation)

From `events.parquet`:

| event_id | user_id | item_id | step | event_type | position | exposure_source |
| -------- | ------- | ------- | ---- | ---------- | -------- | --------------- |
| e_01023  | u_004   | i_012   | 134  | view       | 1        | home_feed       |

---

### 8.2 Multimodal sample spine

`multimodal_samples.parquet`

| sample_id | event_id | user_id | item_id | step | text_ref  | image_ref | audio_ref | tabular_ref |
| --------- | -------- | ------- | ------- | ---- | --------- | --------- | --------- | ----------- |
| s_00001   | e_01023  | u_004   | i_012   | 134  | txt_00001 | img_00001 | aud_00001 | tab_00001   |

**Rule:** `sample_id` is the cross-modal join key.

---

### 8.3 Text modality (LLM-generated, grounded)

`text/samples.jsonl`

```json
{
  "text_id": "txt_00001",
  "sample_id": "s_00001",
  "event_id": "e_01023",
  "content": "I paused on this college because it felt like the kind of place where ambitious students actually thrive—strong research culture, serious expectations.",
  "persona_hint": "ambitious",
  "style": "journal",
  "language": "en"
}
```

This may represent:

* a journal entry
* a reflection
* a narrative caption
* or creative writing (e.g. poetry)

---

### 8.4 Image modality (reference / placeholder)

`images/image_index.csv`

| image_id  | sample_id | item_id | image_type         | path                  |
| --------- | --------- | ------- | ------------------ | --------------------- |
| img_00001 | s_00001   | i_012   | campus_placeholder | images/campus_012.png |

---

### 8.5 Voice-note modality (text surrogate)

`audio/voice_note_index.csv`

| audio_id  | sample_id | transcript_ref | duration_sec |
| --------- | --------- | -------------- | ------------ |
| aud_00001 | s_00001   | txt_00001      | 18           |

Phase 1 stores **textual surrogates** for audio.

---

### 8.6 Tabular modality

`tabular_features.parquet`

| tabular_id | sample_id | user_budget | item_cost | item_prestige | exposure_position |
| ---------- | --------- | ----------- | --------- | ------------- | ----------------- |
| tab_00001  | s_00001   | 0.35        | 0.78      | 0.91          | 1                 |

---

### 8.7 Session context

From `sessions.parquet`:

| session_id | user_id | start_step | end_step |
| ---------- | ------- | ---------- | -------- |
| sess_0012  | u_004   | 130        | 142      |

Implicit linkage:

| sample_id | session_id | within_session_rank |
| --------- | ---------- | ------------------- |
| s_00001   | sess_0012  | 2                   |

---

## 9. LLM usage in this module (important)

LLMs are **explicitly supported** here, but only as **offline generators**.

**LLMs MAY be used for:**

* Interests and self-descriptions
* Journal entries
* Poetry or creative text
* Voice-note transcripts
* Persona-consistent narratives

**LLMs MUST NOT be used for:**

* Simulating behavior
* Creating or modifying events
* Introducing uncached randomness
* Acting as live agents

Once generated, all LLM outputs are **cached, validated, and frozen**.

---

## 10. Determinism requirements

This module **must be deterministic**.

Same inputs + same config + same seed → identical outputs.

Rules:

* All randomness is seed-controlled
* LLM outputs are cached by prompt + schema + seed
* No dependence on wall-clock time

---

## 11. Dependency boundaries

### Upstream

* Simulation outputs (Issues #1 and #3)
* Assembled config (`configs/small.yaml`) built from `configs/checkpoints/*.yaml`
* Module loader: `universal_embedding.synthetic_data.config_loader.load_multimodal_config`

### Downstream

* Phase 2 embedding training pipelines

Downstream code assumes this module is **stable and schema-consistent**.

---

## 12. Definition of Done (DoD)

This issue is complete when:

* [ ] Multimodal schemas are documented
* [ ] LLM-generated content is grounded and reproducible
* [ ] Cross-modal alignment invariants hold
* [ ] Small config run produces full profiles
* [ ] No simulation logic is duplicated
* [ ] PR merged with review

---

## 13. Mental model (remember this)

> **Simulation tells us what happened.
> Multimodal generation tells us how that experience is expressed.**

If you feel tempted to:

* change behavior logic
* add new events
* “fix” distributions

You are probably in the wrong module.

---

## 14. How to work safely in this issue

* Treat simulation outputs as immutable
* Prefer additive changes
* Document schemas before extending
* Keep PRs small
* Ask before adding new modalities

---

This module is where **synthetic humans become multimodal**—without sacrificing rigor, determinism, or scale.
