# Add GPU node readiness evidence gate

GPU runbook sections describe the intended operating procedure, but they do
not prove that an inference node is ready to receive traffic. This offline
gate validates collected evidence for the driver and container runtime, GPU
count, model cache, health checks, GPU metrics, immutable model and rollback
images, rollback readiness, fleet-wide image consistency, and evidence
freshness.

It accepts a JSON array and never contacts a GPU, model provider, or registry:

```bash
python3 scripts/gpu_node_readiness.py \
  examples/gpu-node-readiness.example.json \
  --now 2026-11-22T12:00:00Z
```

A passing result means the supplied evidence satisfies the policy at the
evaluation time and every valid node observation names the same model and
rollback image digests. It does not probe the node or replace an actual
deployment smoke test.

## Portfolio Value

Turns GPU operations guidance into a deterministic readiness contract with a
reviewable rollback boundary, a consistent fleet image boundary, and no paid
provider calls in CI.

## Validation

Run `python3 -m unittest discover -s tests` and confirm a fresh complete node
passes while missing runtime evidence, insufficient GPUs, mutable or identical
image digests, mixed fleet image digests, failed controls, duplicate nodes,
stale evidence, and invalid policy values fail.
