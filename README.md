# Universal Embedding

Synthetic-first system for generating realistic student and college data that will be learned in a shared embedding space.

## Phase 1 goal

Phase 1 builds a deterministic data foundation: define agent schemas, simulate user-item interactions, generate aligned multimodal artifacts, and ground synthetic items in real college structure. The output of Phase 1 is stable, schema-consistent data that Phase 2 can directly consume for embedding learning.

## Project structure and work divisions

Work in Phase 1 is split into issue-owned modules. Each module has a clear boundary and a primary skill set.

| Division (Issue) | Folder | What it owns | Skills and tools needed |
| --- | --- | --- | --- |
| Persona and Agent Design (Issue #1) + Behavior Simulation (Issue #3) | `src/universal_embedding/simulation/` | Persona schemas, population generation, behavior rules, temporal dynamics, event outputs | Schema design, probabilistic modeling, deterministic simulation, config-driven pipelines |
| Multimodal Synthetic Data (Issue #2) | `src/universal_embedding/synthetic_data/` | Multimodal profile generation (text/image/audio surrogates) from simulation outputs | Data orchestration, multimodal alignment, deterministic artifact generation |
| Real College Data Ingestion and Alignment (Issue #4) | `src/universal_embedding/data_ingestion/` | Loading external college data and aligning synthetic items to real institutions | ETL and normalization, schema mapping, ID alignment, reproducibility |

## Sub-workflow inputs and outputs

Each sub-workflow is a contract. Inputs are treated as immutable, and outputs are schema-stable.

| Sub-workflow | Inputs | Outputs |
| --- | --- | --- |
| Simulation | `configs/*.yaml`, schema definitions, seed | `data/synthetic/<run_id>/` with `users.parquet`, `items.parquet`, `events.parquet`, `sessions.parquet`, `metadata.json` |
| Multimodal synthetic data | `data/synthetic/<run_id>/` tables | `data/multimodal/<run_id>/` with `multimodal_samples.parquet`, `text/`, `images/`, `audio/`, `tabular_features.parquet`, `metadata.json` |
| Data ingestion and alignment | `data/external/` raw datasets, `data/synthetic/<run_id>/items.parquet` | `data/processed/colleges/` with `colleges.parquet`, `college_attributes.parquet`, `alignment.(parquet|json)`, `metadata.json` |

## Phase 1 outputs

Phase 1 produces a complete, deterministic dataset suite:

- Synthetic population and interaction logs in `data/synthetic/<run_id>/`
- Multimodal aligned samples in `data/multimodal/<run_id>/`
- Canonical real-college tables and synthetic-to-real alignment in `data/processed/colleges/`
- Metadata that records sources, versions, and seeds for reproducibility

## Connection to Phase 2

Phase 1 outputs are the direct inputs to Phase 2. Phase 2 uses these artifacts to:

- Design universal embedding spaces that capture both students and colleges
- Apply dimensional reduction techniques to make sense of hundreds of input features
- Build neural graph structures with tuned weights and biases (not all inputs matter equally)
- Experiment with different embedding models and architectures

## Quick start

```bash
python -m universal_embedding.pipelines.run_simulation --config configs/small.yaml
python -m universal_embedding.pipelines.build_dataset --config configs/small.yaml
```

## Contributing

See `docs/phase1/` for specs and `docs/phase1/decisions.md` for trade-offs.
