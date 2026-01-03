# Data Schema (Phase 1)

This document defines the Phase 1 data contracts across simulation, multimodal
generation, and real-college ingestion. Schemas are intentionally minimal and
stable; downstream phases can extend but must not break these core fields.

## ID conventions

- All IDs are strings and globally unique within their namespace.
- Simulation run outputs live under `data/synthetic/<run_id>/`.
- Multimodal outputs use the same `<run_id>` under `data/multimodal/<run_id>/`.
- Real college outputs live under `data/processed/colleges/`.

## Simulation outputs (synthetic entities + events)

### `users.parquet` (students / agents)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `user_id` | string | yes | Stable synthetic user identifier. |
| `persona` | string | yes | Persona label (e.g., ambitious, cautious). |
| `ability` | float | yes | Normalized ability/fit signal. |
| `budget` | float | yes | Normalized budget/constraint signal. |

Additional persona attributes may be added as new columns, but must remain
deterministic and schema-stable across runs.

### `items.parquet` (synthetic colleges / items)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `item_id` | string | yes | Stable synthetic item identifier. |
| `prestige` | float | yes | Normalized prestige signal. |
| `cost` | float | yes | Normalized cost signal. |
| `category` | string | yes | Category label (e.g., research, teaching). |

### `events.parquet` (interaction log)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event_id` | string | yes | Unique event identifier. |
| `session_id` | string | yes | Session grouping ID for the event. |
| `user_id` | string | yes | Actor of the event. |
| `item_id` | string | yes | Target item. |
| `step` | int | yes | Deterministic time index. |
| `event_type` | string | yes | Interaction type (view, click, etc.). |
| `position` | int | no | Position shown in list/ranking. |
| `exposure_source` | string | no | Source surface (home_feed, search). |

### `sessions.parquet` (required higher-level grouping)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `session_id` | string | yes | Unique session identifier. |
| `user_id` | string | yes | Session owner. |
| `start_step` | int | yes | First step index in session. |
| `end_step` | int | yes | Last step index in session. |
| `num_events` | int | yes | Count of events in the session. |
| `session_type` | string | no | Session category (browse, decision). |
| `device` | string | no | Device class (mobile, desktop). |
| `entry_source` | string | no | Entry surface (home_feed, search). |

### `metadata.json` (simulation run metadata)

Required keys:

- `run_id` (string)
- `seed` (int)
- `config_path` (string)
- `schema_version` (string)

Additional provenance (e.g., git SHA, dataset version) is allowed but must not
depend on wall-clock time.

## Multimodal outputs (aligned samples)

### `multimodal_samples.parquet`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `sample_id` | string | yes | Cross-modal join key. |
| `event_id` | string | yes | Source event. |
| `user_id` | string | yes | Copied from event. |
| `item_id` | string | yes | Copied from event. |
| `step` | int | yes | Copied from event. |
| `text_ref` | string | yes | Reference into text modality. |
| `image_ref` | string | yes | Reference into image modality. |
| `audio_ref` | string | yes | Reference into audio modality. |
| `tabular_ref` | string | yes | Reference into tabular modality. |

### `text/samples.jsonl`

Each line is a JSON object with:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `text_id` | string | yes | Text artifact identifier. |
| `sample_id` | string | yes | Links to `multimodal_samples`. |
| `event_id` | string | yes | Source event. |
| `content` | string | yes | Deterministic text rendering. |
| `persona_hint` | string | no | Persona conditioning hint. |
| `style` | string | no | Template style tag. |
| `language` | string | no | Language code (e.g., en). |

### `images/image_index.csv`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `image_id` | string | yes | Image artifact identifier. |
| `sample_id` | string | yes | Links to `multimodal_samples`. |
| `item_id` | string | yes | Item depicted. |
| `image_type` | string | yes | Placeholder or type label. |
| `path` | string | yes | Relative path to image asset. |

### `audio/voice_note_index.csv`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `audio_id` | string | yes | Audio artifact identifier. |
| `sample_id` | string | yes | Links to `multimodal_samples`. |
| `transcript_ref` | string | yes | Reference to text transcript. |
| `duration_sec` | int | no | Optional duration in seconds. |

### `tabular_features.parquet`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `tabular_id` | string | yes | Tabular artifact identifier. |
| `sample_id` | string | yes | Links to `multimodal_samples`. |
| `user_budget` | float | yes | Copied/derived from users. |
| `item_cost` | float | yes | Copied/derived from items. |
| `item_prestige` | float | yes | Copied/derived from items. |
| `exposure_position` | int | no | Copied from events. |

Optional session linkage (if emitted) must include `sample_id`, `session_id`,
and an integer `within_session_rank`.

### `metadata.json` (multimodal run metadata)

Required keys mirror simulation metadata:

- `run_id` (string)
- `seed` (int)
- `config_path` (string)
- `schema_version` (string)

## Real college ingestion outputs

### `colleges.parquet` (canonical real colleges)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `college_id` | string | yes | Stable canonical college ID. |
| `name` | string | no | Canonical display name if available. |
| `source_ids` | string | no | Source dataset IDs (serialized). |

The canonical table is the minimal identity surface; structured attributes live
in `college_attributes.parquet`.

### `college_attributes.parquet` (normalized attributes)

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `college_id` | string | yes | Foreign key to `colleges`. |
| `attribute` | string | yes | Attribute name / namespace. |
| `value` | string | yes | Normalized value (string-typed). |
| `value_type` | string | no | Optional type hint (int, float). |
| `source` | string | no | Dataset source identifier. |

### `alignment.parquet` or `alignment.json`

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `item_id` | string | yes | Synthetic item identifier. |
| `college_id` | string | no | Matched real college ID. |
| `match_type` | string | yes | exact, fuzzy, unmatched. |
| `confidence` | float | no | Alignment confidence score. |

Unmatched items must be preserved with `match_type = unmatched`.

### `metadata.json` (ingestion run metadata)

Required keys:

- `schema_version` (string)
- `sources` (array of source names/versions)
- `alignment_method` (string)

## Invariants

- Determinism: same inputs + same config + same seed must yield identical outputs.
- IDs are stable and reused across outputs; no silent dropping of records.
- Alignment decisions are explicit and auditable.
- Multimodal artifacts must reference a valid `sample_id` and `event_id`.
