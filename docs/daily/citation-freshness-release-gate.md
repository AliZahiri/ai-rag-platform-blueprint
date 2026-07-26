# Add citation freshness release gate

<!-- daily-pr-task: citation-freshness-release-gate -->

Traceable citations can still be unsafe to release when their source review is stale or status is unknown. This aggregate gate combines the existing source-identity and freshness policies, requires at least one citation, and prefixes freshness violations with a stable source identifier. It operates on retrieval metadata only and makes no network requests.

## Portfolio Value

Connects citation traceability with review freshness so an answer cannot pass release checks using stale or unidentified evidence.

## Validation

Run `python3 -m unittest discover -s tests` and confirm recent traceable citations pass while empty, stale, unknown-status, duplicate, or unidentified sources fail with source-scoped violations.
