from __future__ import annotations

from urllib.parse import urlsplit


def distinct_source_domains(results: list[dict[str, object]]) -> tuple[str, ...]:
    domains: list[str] = []
    for result in results:
        source_url = result.get("source_url")
        if not isinstance(source_url, str):
            continue
        host = (urlsplit(source_url).hostname or "").lower().rstrip(".")
        if host and host not in domains:
            domains.append(host)
    return tuple(domains)


def retrieval_has_domain_diversity(results: list[dict[str, object]], *, minimum_domains: int = 2) -> bool:
    if not isinstance(minimum_domains, int) or isinstance(minimum_domains, bool) or minimum_domains < 1:
        raise ValueError("minimum domains must be a positive integer")
    return len(distinct_source_domains(results)) >= minimum_domains
