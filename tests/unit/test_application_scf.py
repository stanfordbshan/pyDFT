from __future__ import annotations

from pydft.application.scf import list_preset_dicts, run_calculation_from_payload


def test_run_calculation_from_payload_returns_result() -> None:
    result = run_calculation_from_payload(
        {
            "symbol": "H",
            "parameters": {
                "num_points": 400,
                "max_iterations": 100,
                "xc_model": "LDA",
            },
        }
    )

    assert result.system.symbol == "H"
    assert isinstance(result.total_energy, float)
    assert len(result.density) == 400


def test_list_preset_dicts_contains_hydrogen() -> None:
    presets = list_preset_dicts()
    symbols = {item["symbol"] for item in presets}
    assert "H" in symbols
