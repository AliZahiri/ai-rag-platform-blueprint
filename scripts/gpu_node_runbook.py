from __future__ import annotations

REQUIRED_GPU_RUNBOOK_SECTIONS = (
    "driver_prerequisites",
    "container_runtime",
    "model_cache",
    "health_checks",
    "gpu_metrics",
    "rollback_path",
)


def missing_gpu_runbook_sections(sections: list[str] | tuple[str, ...] | set[str]) -> tuple[str, ...]:
    present = set(sections)
    return tuple(section for section in REQUIRED_GPU_RUNBOOK_SECTIONS if section not in present)


def gpu_runbook_is_complete(sections: list[str] | tuple[str, ...] | set[str]) -> bool:
    return not missing_gpu_runbook_sections(sections)
