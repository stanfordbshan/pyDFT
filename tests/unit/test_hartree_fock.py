from __future__ import annotations

import pytest

from pydft.core.hartree_fock import run_hartree_fock
from pydft.core.models import AtomicSystem, SCFParameters


def test_hf_hydrogen_matches_exact_single_particle_limit() -> None:
    system = AtomicSystem(symbol="H", atomic_number=1, electrons=1)
    params = SCFParameters(
        r_max=30.0,
        num_points=1200,
        max_iterations=120,
        density_mixing=0.3,
        density_tolerance=1e-7,
        xc_model="HF",
    )

    result = run_hartree_fock(system, params)
    assert result.converged
    assert abs(result.total_energy - (-0.5)) < 1.5e-2


def test_hf_rejects_electron_counts_above_supported_scope() -> None:
    system = AtomicSystem(symbol="Li", atomic_number=3, electrons=3)
    params = SCFParameters(xc_model="HF")

    with pytest.raises(ValueError):
        run_hartree_fock(system, params)
