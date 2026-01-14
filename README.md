# Universal Embedding

Synthetic-first system for generating realistic student and college data that will be learned in a shared embedding space.

## Overall project goal

Build a reproducible, synthetic-first dataset and pipeline that can produce realistic student–college interaction data (including multimodal artifacts) to support experimentation with embedding learning and recommendation systems before real users exist.

## Phase 1 goal

Phase 1 builds a deterministic data foundation: define agent schemas, simulate user-item interactions, generate aligned multimodal artifacts, and ground synthetic items in real college structure. The output of Phase 1 is stable, schema-consistent data that Phase 2 can directly consume for embedding learning.

## Project structure and work divisions

Work in Phase 1 is split into issue-owned modules. Each module has a clear boundary and a primary skill set.

| Division (Issue) | Folder | What it owns | Skills and tools needed | Language / libraries |
| --- | --- | --- | --- | --- |
| Persona and Agent Design (Issue #1) + Behavior Simulation (Issue #3) | `src/universal_embedding/simulation/` | Persona schemas, population generation, behavior rules, temporal dynamics, event outputs | Schema design, probabilistic modeling, deterministic simulation, config-driven pipelines | Python (NumPy; dataframe engine like Pandas/Polars; Parquet via PyArrow) |
| Multimodal Synthetic Data (Issue #2) | `src/universal_embedding/synthetic_data/` | Multimodal profile generation (text/image/audio surrogates) from simulation outputs | Data orchestration, schema-constrained LLM generation, multimodal alignment, deterministic caching | Python (LLM provider SDK or local runtime; JSONL; caching; Parquet via PyArrow) |
| Real College Data Ingestion and Alignment (Issue #4) | `src/universal_embedding/data_ingestion/` | Loading external college data and aligning synthetic items to real institutions | ETL and normalization, schema mapping, ID alignment, reproducibility | Python (Pandas/Polars; normalization utilities; fuzzy matching like RapidFuzz) |

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
PYTHONPATH=src python -m universal_embedding.pipelines.run_simulation --config configs/small.yaml
PYTHONPATH=src python -m universal_embedding.pipelines.build_dataset --config configs/small.yaml
```

## Getting started (new teammates)

### 1) Clone the repo

```bash
git clone <GITHUB_REPO_URL>
cd MascotGO-Project-Vectorizing-Our-World
```

### 2) Set up a local Python environment

This project is Python-first (source lives in `src/`). You can use either `venv` or Conda; both work.

**Option A: `venv`**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

**Option B: Conda**

```bash
conda create -n universal-embedding python=3.11 -y
conda activate universal-embedding
python -m pip install -e .
```

If `pip install -e .` fails in your environment, you can still run everything with `PYTHONPATH=src` (shown in the Quick start).

### 3) Environment variables (optional)

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

### 4) Configs and per-person workspaces

`configs/small.yaml` is an assembled config that includes checkpoint configs under `configs/checkpoints/`.

```yaml
includes:
  - checkpoints/00_run_paths.yaml
  - checkpoints/10_population.yaml
  - checkpoints/20_behavior.yaml
  - checkpoints/30_multimodal.yaml
  - checkpoints/40_college_alignment.yaml
```

## Collaboration workflow (issues → branches → PRs)

A branch has been created for you. To
clone a branch that you are working on directly:

```bash
git clone -b <issue-branch> --single-branch <GITHUB_REPO_URL>
cd MascotGO-Project-Vectorizing-Our-World
```

Or, if you already cloned the repo:

```bash
git fetch origin
git checkout <issue-branch>
git pull
```
### Commit guide

Keep commits small and scoped to the Issue boundary (see module READMEs for file ownership rules).

```bash
git status
git add -A
git commit -m "Issue #2: add cached text generator skeleton"
```

### Push and open a PR

```bash
git push -u origin issue-2-multimodal-<short-desc>
```

Then open a Pull Request into `main` and request review from the relevant module owner(s).

### Publish changes to your Issue branch

If you are working directly on an existing Issue branch, push to that same branch:

```bash
git status
git add -A
git commit -m "Issue #<N>: <message>"
git push -u origin <issue-branch>
```
