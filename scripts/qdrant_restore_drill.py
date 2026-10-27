#!/usr/bin/env python3
"""Create and restore a Qdrant collection snapshot into an isolated drill target."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

try:
    from scripts.vector_restore_observation import vector_restore_violations
except ModuleNotFoundError:  # Supports direct execution with `python3 scripts/...`.
    from vector_restore_observation import vector_restore_violations


DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_READY_TIMEOUT_SECONDS = 60.0
COLLECTION_NAME = re.compile(r"[A-Za-z0-9_-]+\Z")


class DrillError(Exception):
    """An input or Qdrant API error that must not expose endpoint details."""


class QdrantHttpError(DrillError):
    def __init__(self, status: int):
        self.status = status
        super().__init__(f"Qdrant returned HTTP {status}")


def normalize_endpoint(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise DrillError("endpoint must be an HTTP(S) origin without credentials or parameters")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def validate_collection_name(value: str, *, label: str) -> str:
    if not COLLECTION_NAME.fullmatch(value):
        raise DrillError(f"{label} must contain only letters, numbers, underscores, or hyphens")
    return value


class QdrantClient:
    def __init__(
        self,
        endpoint: str,
        *,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        if isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
            raise DrillError("timeout must be a positive number")
        self.endpoint = normalize_endpoint(endpoint)
        self.timeout_seconds = timeout_seconds
        self.opener = opener

    def _url(self, path: str) -> str:
        return f"{self.endpoint}{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes]:
        request = Request(self._url(path), data=body, headers=headers or {}, method=method)
        try:
            response = self.opener(request, timeout=self.timeout_seconds)
        except HTTPError as error:
            raise QdrantHttpError(error.code) from error
        except (OSError, URLError) as error:
            raise DrillError(f"Qdrant request failed: {type(error).__name__}") from error
        try:
            status = getattr(response, "status", None)
            if status is None:
                status = response.getcode()
            status = int(status)
            payload = response.read()
        finally:
            if hasattr(response, "close"):
                response.close()
        if not 200 <= status < 300:
            raise QdrantHttpError(status)
        return status, payload

    def json_request(
        self,
        method: str,
        path: str,
        payload: object | None = None,
    ) -> object:
        body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
        _, response = self.request(
            method,
            path,
            body=body,
            headers={"Content-Type": "application/json"} if body is not None else None,
        )
        try:
            decoded = json.loads(response)
        except json.JSONDecodeError as error:
            raise DrillError("Qdrant returned invalid JSON") from error
        if not isinstance(decoded, dict) or decoded.get("status") != "ok" or "result" not in decoded:
            raise DrillError("Qdrant returned an unsuccessful response")
        return decoded["result"]

    def collection_info(self, collection: str) -> dict[str, object]:
        result = self.json_request("GET", f"/collections/{quote(collection, safe='')}")
        if not isinstance(result, dict):
            raise DrillError("Qdrant collection response is invalid")
        return result

    def create_snapshot(self, collection: str) -> str:
        result = self.json_request("POST", f"/collections/{quote(collection, safe='')}/snapshots?wait=true")
        if not isinstance(result, dict) or not isinstance(result.get("name"), str):
            raise DrillError("Qdrant snapshot response did not include a name")
        return result["name"]

    def download_snapshot(self, collection: str, snapshot: str) -> bytes:
        _, archive = self.request(
            "GET",
            f"/collections/{quote(collection, safe='')}/snapshots/{quote(snapshot, safe='')}",
        )
        if not archive:
            raise DrillError("Qdrant returned an empty snapshot")
        return archive

    def upload_snapshot(self, collection: str, archive: bytes) -> None:
        boundary = "qdrant-restore-drill-boundary"
        body = b"".join(
            (
                f"--{boundary}\r\n".encode(),
                b'Content-Disposition: form-data; name="snapshot"; filename="restore.snapshot"\r\n',
                b"Content-Type: application/octet-stream\r\n\r\n",
                archive,
                f"\r\n--{boundary}--\r\n".encode(),
            )
        )
        _, response = self.request(
            "POST",
            f"/collections/{quote(collection, safe='')}/snapshots/upload?priority=snapshot&wait=true",
            body=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        try:
            decoded = json.loads(response)
        except json.JSONDecodeError as error:
            raise DrillError("Qdrant returned invalid JSON after snapshot upload") from error
        if not isinstance(decoded, dict) or decoded.get("status") != "ok":
            raise DrillError("Qdrant rejected the uploaded snapshot")

    def point_count(self, collection: str) -> int:
        result = self.json_request(
            "POST", f"/collections/{quote(collection, safe='')}/points/count", {"exact": True}
        )
        count = result.get("count") if isinstance(result, dict) else None
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise DrillError("Qdrant count response is invalid")
        return count

    def sample_vector(self, collection: str) -> tuple[str | None, list[float]]:
        result = self.json_request(
            "POST",
            f"/collections/{quote(collection, safe='')}/points/scroll",
            {"limit": 1, "with_vector": True, "with_payload": False},
        )
        points = result.get("points") if isinstance(result, dict) else None
        if not isinstance(points, list) or not points or not isinstance(points[0], dict):
            raise DrillError("source collection must contain a point for the similarity check")
        vector = points[0].get("vector")
        if isinstance(vector, list) and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in vector):
            return None, [float(value) for value in vector]
        if isinstance(vector, dict) and len(vector) == 1:
            name, values = next(iter(vector.items()))
            if isinstance(name, str) and isinstance(values, list) and all(
                isinstance(value, (int, float)) and not isinstance(value, bool) for value in values
            ):
                return name, [float(value) for value in values]
        raise DrillError("source point has no usable vector")

    def sample_query_passes(self, collection: str, vector_name: str | None, vector: list[float]) -> bool:
        query: dict[str, object] = {"limit": 1, "with_payload": False, "with_vector": False}
        query["vector"] = vector if vector_name is None else {"name": vector_name, "vector": vector}
        result = self.json_request(
            "POST", f"/collections/{quote(collection, safe='')}/points/search", query
        )
        return isinstance(result, list) and bool(result)


def vector_dimension(collection: dict[str, object]) -> int:
    try:
        vectors = collection["config"]["params"]["vectors"]  # type: ignore[index]
    except (KeyError, TypeError):
        raise DrillError("Qdrant collection does not declare vector parameters") from None
    if isinstance(vectors, dict) and isinstance(vectors.get("size"), int):
        return vectors["size"]
    if isinstance(vectors, dict) and len(vectors) == 1:
        candidate = next(iter(vectors.values()))
        if isinstance(candidate, dict) and isinstance(candidate.get("size"), int):
            return candidate["size"]
    raise DrillError("Qdrant collection vector dimension is invalid or ambiguous")


def restore_observation(
    source: QdrantClient,
    target: QdrantClient,
    *,
    source_collection: str,
    target_collection: str,
    ready_timeout_seconds: float = DEFAULT_READY_TIMEOUT_SECONDS,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    if source.endpoint == target.endpoint:
        raise DrillError("source and restore endpoints must differ")
    if isinstance(ready_timeout_seconds, bool) or ready_timeout_seconds <= 0:
        raise DrillError("ready timeout must be a positive number")

    source_info = source.collection_info(source_collection)
    expected_count = source.point_count(source_collection)
    if expected_count <= 0:
        raise DrillError("source collection must contain at least one point for the drill")
    sample_name, sample_vector = source.sample_vector(source_collection)
    try:
        target.collection_info(target_collection)
    except QdrantHttpError as error:
        if error.status != 404:
            raise
    else:
        raise DrillError("restore target collection already exists; use a fresh isolated target")

    snapshot_name = source.create_snapshot(source_collection)
    archive = source.download_snapshot(source_collection, snapshot_name)
    digest = hashlib.sha256(archive).hexdigest()
    target.upload_snapshot(target_collection, archive)

    deadline = time.monotonic() + ready_timeout_seconds
    while True:
        try:
            target_info = target.collection_info(target_collection)
            break
        except QdrantHttpError as error:
            if error.status != 404 or time.monotonic() >= deadline:
                raise
            sleep(1)

    restored_count = target.point_count(target_collection)
    verified_at = now()
    if verified_at.tzinfo is None or verified_at.utcoffset() is None:
        raise DrillError("clock must return a timezone-aware timestamp")
    observation = {
        "expected_record_count": expected_count,
        "restored_record_count": restored_count,
        "expected_dimension": vector_dimension(source_info),
        "restored_dimension": vector_dimension(target_info),
        "expected_manifest_sha256": digest,
        "restored_manifest_sha256": digest,
        "sample_query_passed": target.sample_query_passes(target_collection, sample_name, sample_vector),
        "verified_at": verified_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return observation


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an isolated Qdrant snapshot restore drill.")
    parser.add_argument("--source-url", default="http://localhost:6333")
    parser.add_argument("--restore-url", default="http://localhost:6334")
    parser.add_argument("--collection", required=True, help="Existing source collection name")
    parser.add_argument("--restore-collection", help="Fresh target collection name; defaults to --collection")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--ready-timeout-seconds", type=float, default=DEFAULT_READY_TIMEOUT_SECONDS)
    parser.add_argument("--output", type=Path, help="Write the restore observation JSON to this path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        source_collection = validate_collection_name(args.collection, label="collection")
        target_collection = validate_collection_name(
            args.restore_collection or source_collection, label="restore collection"
        )
        observation = restore_observation(
            QdrantClient(args.source_url, timeout_seconds=args.timeout_seconds),
            QdrantClient(args.restore_url, timeout_seconds=args.timeout_seconds),
            source_collection=source_collection,
            target_collection=target_collection,
            ready_timeout_seconds=args.ready_timeout_seconds,
        )
        violations = vector_restore_violations(
            observation, now=datetime.now(timezone.utc), maximum_age_seconds=300
        )
        if args.output:
            args.output.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (DrillError, OSError) as error:
        print(json.dumps({"error": str(error), "status": "error"}, sort_keys=True), file=sys.stderr)
        return 2

    encoded = json.dumps(observation, indent=2, sort_keys=True)
    print(encoded)
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
