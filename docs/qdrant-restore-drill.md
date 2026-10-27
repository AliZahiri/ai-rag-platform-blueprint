# Qdrant restore drill

This drill creates a collection snapshot on the local Qdrant service, restores it
to a separate empty Qdrant instance, and writes the observation consumed by
`scripts/vector_restore_observation.py`. It does not call an LLM provider.

The target service is deliberately isolated in the `restore-drill` Compose
profile. The CLI rejects equal source and target endpoints, rejects a pre-existing
target collection, and never deletes collections or snapshots. Do not point the
restore URL at a shared or production Qdrant instance.

## Prerequisites

Start the normal stack and the isolated restore target. Replace `knowledge` with
an existing, non-empty collection that has at least one vector.

```bash
docker compose -f compose/docker-compose.yml --env-file .env up -d vector-db
docker compose --project-name rag-restore-drill \
  -f compose/docker-compose.yml --env-file .env --profile restore-drill \
  up -d vector-restore-drill

python3 scripts/qdrant_restore_drill.py \
  --collection knowledge \
  --source-url http://localhost:6333 \
  --restore-url http://localhost:6334 \
  --output qdrant-restore-observation.json
```

The output records the source and restored point counts, vector dimensions, the
SHA-256 digest of the transferred snapshot, a sample similarity query result, and
a UTC verification timestamp. A successful command exits with `0`; a completed
drill that fails the evidence policy exits with `1`; invalid input or an API
failure exits with `2`.

Validate the resulting evidence with the existing offline release gate:

```bash
python3 scripts/vector_restore_observation.py \
  qdrant-restore-observation.json \
  --maximum-age-seconds 300
```

## Repeating the drill

Each run requires an empty target collection. Inspect the observation first, then
reset the dedicated drill project before a new run:

```bash
docker compose --project-name rag-restore-drill \
  -f compose/docker-compose.yml --env-file .env --profile restore-drill down -v
```

That command removes only the dedicated restore-drill project's target volume.

The source-side snapshot is retained intentionally. Archive or delete it through
your approved retention procedure after recording the drill result.
