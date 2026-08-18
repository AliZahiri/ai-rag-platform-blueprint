# Model latency budget gate

Provider calls should be admitted and evaluated against an explicit latency budget. This offline helper validates request identifiers and non-negative response latency without contacting a paid provider. It provides a deterministic CI contract for route-level SLO evidence.
