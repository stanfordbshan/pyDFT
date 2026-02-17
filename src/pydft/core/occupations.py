"""Helpers to assign electrons to Kohn-Sham states."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class RadialState:
    """One radial Kohn-Sham state for fixed (n_index, l)."""

    n_index: int
    l: int
    energy: float
    orbital: np.ndarray


@dataclass(slots=True)
class OccupiedState:
    """Radial state with assigned occupancy."""

    state: RadialState
    occupancy: float


def fill_occupations(states: list[RadialState], electrons: int) -> list[OccupiedState]:
    """Fill orbitals by increasing energy with spin/azimuthal degeneracy.

    Capacity per state group with angular momentum l is 2*(2*l+1).
    """

    remaining = float(electrons)
    occupied: list[OccupiedState] = []

    for state in sorted(states, key=lambda item: item.energy):
        if remaining <= 0:
            break
        capacity = float(2 * (2 * state.l + 1))
        occ = min(capacity, remaining)
        if occ > 0:
            occupied.append(OccupiedState(state=state, occupancy=occ))
            remaining -= occ

    if remaining > 1.0e-8:
        raise ValueError(
            "Not enough basis states to place all electrons. Increase l_max or states_per_l."
        )

    return occupied
