# Universal Embedding

Synthetic-first simulation system for generating realistic student and college data in a shared embedding space.

## Phase 1 focus
- Define schemas and assumptions
- Simulate personas and behaviors
- Generate multimodal artifacts
- Validate realism and quality

## Quick start
```bash
python -m universal_embedding.pipelines.run_simulation --config configs/small.yaml
python -m universal_embedding.pipelines.build_dataset --config configs/small.yaml
```

## Contributing
See `docs/phase1/` for specs and `docs/phase1/decisions.md` for trade-offs.
