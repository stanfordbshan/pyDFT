"""Shared payload mapping and validation utilities.

This module is transport-independent and is reused by API, GUI bridge,
and CLI adapters to keep request behavior consistent.
"""

from __future__ import annotations

from typing import Any, Mapping

from .models import AtomicSystem, SCFParameters
from .presets import build_system


def parse_request_payload(payload: Mapping[str, Any]) -> tuple[AtomicSystem, SCFParameters]:
    """Parse a generic request payload into typed system/parameter objects."""

    symbol = payload.get("symbol", "He")
    atomic_number = _optional_int(payload.get("atomic_number"))
    electrons = _optional_int(payload.get("electrons"))

    params_data = payload.get("parameters", {})
    if params_data is None:
        params_data = {}
    if not isinstance(params_data, Mapping):
        raise ValueError("'parameters' must be an object")

    xc_model = str(params_data.get("xc_model", "LDA")).strip().upper()
    if xc_model not in {"LDA", "LSDA", "HF"}:
        raise ValueError("parameters.xc_model must be one of 'LDA', 'LSDA', or 'HF'")

    spin_polarization = _optional_float(params_data.get("spin_polarization"))
    if spin_polarization is not None and (spin_polarization < -1.0 or spin_polarization > 1.0):
        raise ValueError("parameters.spin_polarization must be between -1 and 1")

    if xc_model == "LDA":
        # LDA is spin-unpolarized, so zeta is ignored even if provided.
        spin_polarization = None

    use_hartree = bool(params_data.get("use_hartree", True))
    use_exchange = bool(params_data.get("use_exchange", True))
    use_correlation = bool(params_data.get("use_correlation", True))

    if xc_model == "HF":
        # Pure HF for this educational module.
        use_hartree = True
        use_exchange = True
        use_correlation = False

    system = build_system(symbol=symbol, atomic_number=atomic_number, electrons=electrons)
    params = SCFParameters(
        r_max=float(params_data.get("r_max", 20.0)),
        num_points=int(params_data.get("num_points", 1200)),
        max_iterations=int(params_data.get("max_iterations", 200)),
        density_mixing=float(params_data.get("density_mixing", 0.3)),
        density_tolerance=float(params_data.get("density_tolerance", 1e-6)),
        l_max=int(params_data.get("l_max", 1)),
        states_per_l=int(params_data.get("states_per_l", 4)),
        use_hartree=use_hartree,
        use_exchange=use_exchange,
        use_correlation=use_correlation,
        xc_model=xc_model,
        spin_polarization=spin_polarization,
    )

    return system, params


def _optional_int(value: Any) -> int | None:
    """Return integer value or None, preserving None-like inputs."""

    if value is None:
        return None
    return int(value)


def _optional_float(value: Any) -> float | None:
    """Return float value or None, preserving None/blank inputs."""

    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return float(value)
