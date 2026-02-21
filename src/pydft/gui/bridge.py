"""pywebview bridge API exposed to JavaScript.

This layer keeps the GUI independent from solver internals by forwarding
requests into transport-agnostic application use cases.
"""

from __future__ import annotations

import json
from urllib import error as urllib_error
from urllib import request as urllib_request
from typing import Any, Mapping

from pydft.application.scf import list_preset_dicts, run_calculation_from_payload


class ThinkBridge:
    """Bridge object registered as `js_api` in pywebview."""

    DEFAULT_API_BASE = "http://127.0.0.1:8000"

    def health(self, _payload: Any | None = None) -> dict[str, str]:
        """Simple liveness check callable from JavaScript."""

        return {"status": "ok"}

    def get_presets(self, _payload: Any | None = None) -> list[dict[str, Any]]:
        """Return available simple-system presets for the UI dropdown."""

        return list_preset_dicts()

    def run_scf(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Run one SCF calculation from a JS-provided payload.

        Accepted forms:
        1. Legacy direct mode:
           ``{"symbol": "...", "parameters": {...}}``
        2. Mode-aware:
           ``{"mode": "direct|api|auto", "api_base": "...", "request": {...}}``
        """

        mode, api_base, request_payload = self._decode_mode_payload(payload)

        if mode == "direct":
            result = self._run_scf_direct(request_payload)
            result["_execution_path"] = "direct"
            return result
        if mode == "api":
            result = self._run_scf_via_api(request_payload, api_base=api_base)
            result["_execution_path"] = "api"
            return result
        if mode == "auto":
            try:
                result = self._run_scf_direct(request_payload)
                result["_execution_path"] = "direct"
                return result
            except Exception as direct_exc:
                try:
                    result = self._run_scf_via_api(request_payload, api_base=api_base)
                    result["_execution_path"] = "api-fallback"
                    return result
                except Exception as api_exc:
                    raise RuntimeError(
                        "Auto mode failed: direct execution error was "
                        f"'{direct_exc}', and API fallback error was '{api_exc}'."
                    ) from api_exc

        raise ValueError("mode must be one of 'direct', 'api', or 'auto'")

    def _decode_mode_payload(
        self,
        payload: Mapping[str, Any],
    ) -> tuple[str, str, Mapping[str, Any]]:
        """Normalize payload into (mode, api_base, request_payload)."""

        mode = "direct"
        api_base = self.DEFAULT_API_BASE
        request_payload: Mapping[str, Any] = payload

        if "request" in payload:
            candidate = payload.get("mode", "auto")
            mode = str(candidate).strip().lower()
            api_base = str(payload.get("api_base", self.DEFAULT_API_BASE))
            request = payload.get("request")
            if not isinstance(request, Mapping):
                raise ValueError("payload.request must be an object")
            request_payload = request

        return mode, api_base, request_payload

    def _run_scf_direct(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Run calculation in-process through application use case."""

        result = run_calculation_from_payload(payload)
        return result.to_dict()

    def _run_scf_via_api(self, payload: Mapping[str, Any], api_base: str) -> dict[str, Any]:
        """Run calculation by forwarding payload to a remote HTTP API."""

        endpoint = f"{api_base.rstrip('/')}/api/v1/scf"
        body = json.dumps(payload).encode("utf-8")
        request = urllib_request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib_request.urlopen(request, timeout=10.0) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib_error.HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"API request failed ({exc.code}): {detail}") from exc
        except urllib_error.URLError as exc:
            raise RuntimeError(f"API request failed: {exc.reason}") from exc
