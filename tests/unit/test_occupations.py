from __future__ import annotations

import numpy as np
import pytest

from pydft.methods.atomic.occupations import RadialState, fill_occupations


def test_fill_occupations_respects_degeneracy() -> None:
    orbital = np.ones(16)
    states = [
        RadialState(n_index=1, l=0, energy=-0.90, orbital=orbital),
        RadialState(n_index=1, l=1, energy=-0.35, orbital=orbital),
        RadialState(n_index=2, l=0, energy=-0.15, orbital=orbital),
    ]

    occupied = fill_occupations(states, electrons=4)
    assert len(occupied) == 2
    assert occupied[0].state.l == 0
    assert occupied[0].occupancy == 2.0
    assert occupied[1].state.l == 1
    assert occupied[1].occupancy == 2.0


def test_fill_occupations_raises_when_states_are_insufficient() -> None:
    states = [RadialState(n_index=1, l=0, energy=-0.90, orbital=np.ones(10))]
    with pytest.raises(ValueError):
        fill_occupations(states, electrons=4)


def test_fill_occupations_supports_single_spin_channel_capacity() -> None:
    orbital = np.ones(16)
    states = [RadialState(n_index=1, l=1, energy=-0.40, orbital=orbital)]

    occupied = fill_occupations(states, electrons=2, spin_channels=1)
    assert len(occupied) == 1
    assert occupied[0].occupancy == 2.0
