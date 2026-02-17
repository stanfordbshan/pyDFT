"""Preset systems and system-construction helpers."""

from __future__ import annotations

from dataclasses import replace

from .models import AtomicSystem

_PRESETS: dict[str, AtomicSystem] = {
    "H": AtomicSystem(symbol="H", atomic_number=1, electrons=1, description="Hydrogen atom"),
    "H-": AtomicSystem(
        symbol="H-",
        atomic_number=1,
        electrons=2,
        description="Hydride anion model system",
    ),
    "He": AtomicSystem(symbol="He", atomic_number=2, electrons=2, description="Helium atom"),
    "He+": AtomicSystem(
        symbol="He+",
        atomic_number=2,
        electrons=1,
        description="Helium ion with one electron",
    ),
    "Li": AtomicSystem(
        symbol="Li",
        atomic_number=3,
        electrons=3,
        description="Lithium atom",
    ),
    "Be": AtomicSystem(
        symbol="Be",
        atomic_number=4,
        electrons=4,
        description="Beryllium atom",
    ),
    "Ne": AtomicSystem(
        symbol="Ne",
        atomic_number=10,
        electrons=10,
        description="Neon atom",
    ),
}


def available_presets() -> list[AtomicSystem]:
    """Return a copy of bundled simple-system presets."""

    return [replace(system) for system in _PRESETS.values()]


def build_system(
    symbol: str | None = "He",
    atomic_number: int | None = None,
    electrons: int | None = None,
) -> AtomicSystem:
    """Construct an AtomicSystem from a preset and/or explicit overrides."""

    if symbol is not None and symbol in _PRESETS:
        base = replace(_PRESETS[symbol])
    else:
        base = AtomicSystem(
            symbol=symbol or "Custom",
            atomic_number=atomic_number or 2,
            electrons=electrons or 2,
            description="Custom atom-like system",
        )

    if atomic_number is not None:
        base.atomic_number = atomic_number
    if electrons is not None:
        base.electrons = electrons

    if base.atomic_number <= 0:
        raise ValueError("atomic_number must be positive")
    if base.electrons <= 0:
        raise ValueError("electrons must be positive")

    return base
