# Real College Data Ingestion & Alignment (Issue #4)

**Phase:** 1 — Simulation & Synthetic Data
**Primary folder:** `src/universal_embedding/data_ingestion/`

---

## 1. What this issue is about (TL;DR)

This module **grounds the synthetic simulation in real-world institutional structure**.

It answers one core question:

> **How do we ingest real college datasets and align them with synthetic items in a schema-consistent, reproducible way?**

This issue ensures that **synthetic items are not floating abstractions**, but can be mapped to real colleges, enabling more realistic and transferable embeddings in Phase 2.

---

## 2. High-level goal

Produce a **canonical, normalized representation of real colleges** and a **stable alignment** between:

* real-world college datasets
* synthetic `items.parquet` produced by simulation

while preserving:

* reproducibility
* schema stability
* explainability of alignment decisions

---

## 3. What this module does

This module is responsible for:

* Loading external college datasets (e.g. scorecards, rankings, metadata)
* Defining canonical schemas for real colleges
* Normalizing heterogeneous raw features
* Aligning synthetic items to real colleges via stable IDs
* Producing explicit alignment mappings and metadata

---

## 4. What this module does NOT do

This module explicitly does **NOT**:

* ❌ Modify simulation outputs
* ❌ Generate synthetic users, items, or events
* ❌ Perform feature engineering for models
* ❌ Train or evaluate embeddings
* ❌ Silently drop or overwrite unmatched records

All alignment decisions must be **explicit and auditable**.

---

## 5. Folder structure & ownership

```
data_ingestion/
├─ README.md          # this file
├─ loaders.py         # external dataset loaders
├─ schemas.py         # canonical college schemas
├─ normalization.py   # feature cleaning & normalization
└─ alignment.py       # synthetic ↔ real mapping logic
```

> This issue owns **all files in this folder**.

---

## 6. Inputs (DO NOT BREAK)

### External inputs

* Real college datasets (e.g. College Scorecard, rankings, institutional metadata)
* Stored or referenced under:

```
data/external/
```

Raw external data **must remain immutable**.

---

### Synthetic inputs

| File            | Source                     |
| --------------- | -------------------------- |
| `items.parquet` | `data/synthetic/<run_id>/` |

Assumptions:

* `item_id` is stable
* Synthetic schemas must not be modified
* Missing alignments are expected and must be handled explicitly

---

## 7. Outputs (contract)

### Output location

```
data/processed/colleges/
```

### Required outputs

| File                                    | Purpose                                        |
| --------------------------------------- | ---------------------------------------------- |
| `colleges.parquet`                      | Canonical table of real colleges               |
| `college_attributes.parquet`            | Normalized, structured features                |
| `alignment.parquet` or `alignment.json` | Mapping between `item_id` and real college IDs |
| `metadata.json`                         | Data sources, versions, timestamps             |

---

### Alignment mapping (example)

| item_id | college_id | match_type | confidence |
| ------- | ---------- | ---------- | ---------- |
| i_012   | c_045      | exact      | 1.00       |
| i_031   | c_102      | fuzzy      | 0.82       |
| i_077   | NULL       | unmatched  | NULL       |

Rules:

* Unmatched records **must be retained and logged**
* Confidence and match type must be explicit
* No silent coercion or dropping

---

## 8. Determinism & reproducibility

This module **must be deterministic**.

> Same external inputs + same config → identical outputs

Requirements:

* Config-driven file paths
* No dependence on wall-clock time
* Stable sorting and ID generation
* Version metadata recorded

---

## 9. Dependency boundaries

### Upstream dependencies

* External raw datasets
* Simulation output (`items.parquet`)

### Downstream consumers

* `synthetic_data.dataset_builder`
* `evaluation.distribution`
* Phase 2 embedding training pipelines

Downstream code assumes:

* schemas are stable
* alignment mappings are explicit

---

## 10. Definition of Done (DoD)

This issue is complete when:

* [ ] External datasets are ingested via reproducible loaders
* [ ] Canonical college schema is defined and validated
* [ ] Synthetic items are aligned to real colleges with stable IDs
* [ ] Unmatched or ambiguous cases are explicitly handled
* [ ] Outputs are deterministic and documented
* [ ] PR merged with review

---

## 11. Mental model (important)

> **Simulation defines abstract items.
> This module tells us which real institutions those items correspond to.**

If you feel tempted to:

* tweak simulation distributions
* “fix” item attributes
* add behavior logic

You are in the **wrong module**.

---

## 12. How to work safely in this issue

* Treat `data/external/` as read-only
* Never modify synthetic schemas
* Prefer transparent alignment rules over clever heuristics
* Log and document all assumptions
* Keep PRs small and reviewable
