# Add opt-in provider liveness probe

<!-- daily-pr-task: opt-in-provider-liveness-probe -->

Provider liveness checks must remain disabled by default so CI never makes paid or credential-bearing requests. The helper returns structured status, rejects endpoints containing user information, query strings, or fragments, bounds the timeout, and accepts an injected opener for deterministic tests. Operators must explicitly enable a probe and should target an unauthenticated health endpoint rather than a completion API.

## Portfolio Value

Adds a production-oriented provider readiness signal while proving that default CI performs no provider calls and endpoint metadata cannot leak credentials.

## Validation

Run `python3 -m unittest discover -s tests` and confirm disabled probes make no network call while unsafe endpoints, bounded timeouts, and structured success are covered.
