"""pywebview bridge API exposed to JavaScript.

This layer keeps the GUI independent from solver internals by forwarding
requests into the core parser/engine modules.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from pydft.core.dft_engine import run_scf
from pydft.core.parser import parse_request_payload
from pydft.core.presets import available_presets


class ThinkBridge:
    """Bridge object registered as `js_api` in pywebview."""

    def health(self, _payload: Any | None = None) -> dict[str, str]:
        """Simple liveness check callable from JavaScript."""

        return {"status": "ok"}

    def get_presets(self, _payload: Any | None = None) -> list[dict[str, Any]]:
        """Return available simple-system presets for the UI dropdown."""

        return [asdict(system) for system in available_presets()]

    def run_scf(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Run one SCF calculation from a JS-provided payload."""

        system, params = parse_request_payload(payload)
        result = run_scf(system, params)
        return result.to_dict()
