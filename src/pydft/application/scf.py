"""Transport-agnostic SCF use cases."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from pydft.core.models import AtomicSystem, SCFParameters, SCFResult
from pydft.core.presets import available_presets
from pydft.core.request_mapper import parse_request_payload
from pydft.methods.atomic.dft_engine import run_scf


def run_calculation(system: AtomicSystem, params: SCFParameters) -> SCFResult:
    """Run one typed SCF calculation."""

    return run_scf(system, params)


def run_calculation_from_payload(payload: Mapping[str, Any]) -> SCFResult:
    """Run one SCF calculation from a transport-neutral payload."""

    system, params = parse_request_payload(payload)
    return run_calculation(system, params)


def list_presets() -> list[AtomicSystem]:
    """Return available preset systems as typed domain objects."""

    return available_presets()


def list_preset_dicts() -> list[dict[str, Any]]:
    """Return preset systems in JSON-serializable dictionary form."""

    return [asdict(system) for system in list_presets()]
