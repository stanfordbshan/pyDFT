from __future__ import annotations

import pytest

from pydft.gui.bridge import ThinkBridge


def _sample_payload() -> dict:
    return {
        "symbol": "H",
        "parameters": {
            "num_points": 300,
            "max_iterations": 80,
            "xc_model": "LDA",
        },
    }


def test_bridge_direct_mode_runs_in_process() -> None:
    bridge = ThinkBridge()
    result = bridge.run_scf({"mode": "direct", "request": _sample_payload()})
    assert result["system"]["symbol"] == "H"
    assert result["_execution_path"] == "direct"


def test_bridge_api_mode_calls_api_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    bridge = ThinkBridge()

    def fake_api(payload: dict, api_base: str) -> dict:
        return {"system": {"symbol": payload["symbol"]}, "_execution_path": "api"}

    monkeypatch.setattr(bridge, "_run_scf_via_api", fake_api)
    result = bridge.run_scf({"mode": "api", "api_base": "http://example", "request": _sample_payload()})
    assert result["_execution_path"] == "api"
    assert result["system"]["symbol"] == "H"


def test_bridge_auto_mode_falls_back_to_api(monkeypatch: pytest.MonkeyPatch) -> None:
    bridge = ThinkBridge()

    def fail_direct(_payload: dict) -> dict:
        raise RuntimeError("direct failed")

    def fake_api(payload: dict, api_base: str) -> dict:
        return {"system": {"symbol": payload["symbol"]}, "_execution_path": "api-fallback"}

    monkeypatch.setattr(bridge, "_run_scf_direct", fail_direct)
    monkeypatch.setattr(bridge, "_run_scf_via_api", fake_api)

    result = bridge.run_scf({"mode": "auto", "api_base": "http://example", "request": _sample_payload()})
    assert result["_execution_path"] == "api-fallback"


def test_bridge_rejects_invalid_mode() -> None:
    bridge = ThinkBridge()
    with pytest.raises(ValueError):
        bridge.run_scf({"mode": "invalid", "request": _sample_payload()})
