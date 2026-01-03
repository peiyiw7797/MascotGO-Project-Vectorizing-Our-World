#!/usr/bin/env bash
set -euo pipefail

python -m universal_embedding.pipelines.run_simulation --config configs/large.yaml
python -m universal_embedding.pipelines.build_dataset --config configs/large.yaml
