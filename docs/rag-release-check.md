# Unified RAG Release Check

The unified release check runs the repository's core offline policy gates from
one versioned manifest and emits one JSON result for CI, release evidence, or
operator review. It does not contact model providers.

## Run the example

From the repository root:

```bash
python3 scripts/rag_release_check.py examples/release-checks.example.json
```

Paths passed in each check's `args` are resolved from the manifest directory.
The example covers route validation, citation freshness, retention, vector
backup verification, and multi-replica index consistency.

## Manifest contract

Version 1 is described by
[`schemas/rag-release-check-manifest.v1.schema.json`](../schemas/rag-release-check-manifest.v1.schema.json).
Every check requires a unique lowercase `id`, an allowlisted `gate`, and the
gate's normal arguments. Unknown fields, unknown gates, duplicate IDs, and
unsupported schema versions fail before any gate runs.

The runner executes gates directly with the current Python interpreter; it does
not invoke a shell or accept executable paths from the manifest. Each gate has a
30-second timeout by default, configurable with `--timeout-seconds`.

## Result and exit codes

The aggregate JSON contains every gate's exit code and parsed report plus a
summary. Status precedence is `error`, then `fail`, then `pass`:

- `0`: every gate passed;
- `1`: at least one policy gate rejected the release and no execution error occurred;
- `2`: the manifest was invalid, a gate timed out or failed to execute, or a gate did not emit a JSON object.

Archive the JSON output as release evidence. Treat manifests as reviewed
configuration: a manifest can select arguments such as input files or an
explicit live-probe option supported by a gate. The provided example stays
fully offline and does not require provider credentials.
