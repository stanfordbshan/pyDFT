from __future__ import annotations

from pydft.core.presets import available_presets, build_system


def test_available_presets_include_common_atoms() -> None:
    symbols = {system.symbol for system in available_presets()}
    assert {"H", "He", "He+", "Li", "Be", "Ne"}.issubset(symbols)


def test_build_system_uses_preset_values() -> None:
    system = build_system(symbol="Li")
    assert system.atomic_number == 3
    assert system.electrons == 3
