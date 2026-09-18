# Immutable Compose Image Pinning

The blueprint pins every default Compose image to a multi-platform OCI index
digest. This makes the default deployment reproducible: a tag can move, but an
image digest always selects the reviewed artifact. Environment variables remain
available as an explicit upgrade mechanism; production overrides must also use
digest-pinned references.

## Current lock set

The following tag-to-digest resolutions were verified on 2026-09-18 with
`docker buildx imagetools inspect`:

| Component | Reviewed source tag | Pinned OCI index digest |
| --- | --- | --- |
| PostgreSQL | `postgres:16-alpine` | `sha256:3c5c8892d184f738f4fe282d14ddaa613a38f00f4189d2d94725ebe6f2909ddb` |
| Redis | `redis:7-alpine` | `sha256:520775a41a63e77e06c73e35d2fd9cc15921a609516818796b4ecbb813078bc7` |
| Qdrant | `qdrant/qdrant:latest` | `sha256:12364fe851b9f17356fc88189fc06d1b521262e04659ec7345975b00c9246a10` |
| LiteLLM | `ghcr.io/berriai/litellm:main-latest` | `sha256:52abe19ecef09d149abd23f8a4aed6683dd7f780f90a0c20d214dfb29006f2dd` |
| Prometheus | `prom/prometheus:v2.54.1` | `sha256:f6639335d34a77d9d9db382b92eeb7fc00934be8eae81dbc03b31cfe90411a94` |
| Grafana | `grafana/grafana:11.1.4` | `sha256:886b56d5534e54f69a8cfcb4b8928da8fc753178a7a3d20c3f9b04b660169805` |

The tag is recorded for review context only. The Compose default and example
environment file use the digest, not a mutable tag.

## Validation

Run the offline validator from the repository root:

```bash
python3 scripts/compose_image_pinning.py \
  --compose compose/docker-compose.yml \
  --env env/.env.example \
  --json
```

It rejects unpinned defaults, missing environment entries, unpinned overrides,
or drift between an override and the Compose fallback. It parses only the
project's `image: ${VARIABLE:-digest}` convention and does not contact a
registry.

## Upgrade workflow

1. Select a reviewed upstream version; never promote `latest` or `main-latest`
   solely because it changed.
2. Resolve and review the multi-platform index with
   `docker buildx imagetools inspect <image:tag>`.
3. Update the identical digest in `compose/docker-compose.yml` and
   `env/.env.example`, then update the source-tag record above.
4. Run the validator, `docker compose -f compose/docker-compose.yml --env-file
   env/.env.example config`, and the unit suite.
5. Review upstream compatibility, security advisories, release notes, and a
   rollback plan before deployment. Keep the prior digest available for
   rollback.

Pinning identifies the artifact but does not attest to its security or replace
signature verification, vulnerability review, or registry access controls.
