"""Benchmark checks against reference values from standard literature data sources."""

from __future__ import annotations

from pydft.core.models import AtomicSystem, SCFParameters
from pydft.core.dft_engine import run_scf


def test_hydrogen_single_particle_benchmark() -> None:
    """Hydrogen 1s exact non-relativistic reference: -0.5 Ha.

    This benchmark disables Hartree and XC to isolate the radial solver.
    """

    system = AtomicSystem(symbol="H", atomic_number=1, electrons=1)
    params = SCFParameters(
        r_max=35.0,
        num_points=1200,
        max_iterations=20,
        density_mixing=0.5,
        density_tolerance=1e-10,
        l_max=0,
        states_per_l=2,
        use_hartree=False,
        use_exchange=False,
        use_correlation=False,
    )

    result = run_scf(system, params)

    assert abs(result.total_energy - (-0.5)) < 1.5e-2


def test_helium_lda_benchmark_against_nist_range() -> None:
    """He LDA total energy benchmark against NIST LDA table.

    NIST reports Etot(LDA) = -2.834836 Hartree for Helium.
    A wider tolerance is used because this educational solver uses a simple
    finite-difference radial discretization and a different practical setup.
    """

    system = AtomicSystem(symbol="He", atomic_number=2, electrons=2)
    params = SCFParameters(
        r_max=28.0,
        num_points=1400,
        max_iterations=220,
        density_mixing=0.25,
        density_tolerance=2e-6,
        l_max=1,
        states_per_l=5,
        use_hartree=True,
        use_exchange=True,
        use_correlation=True,
    )

    result = run_scf(system, params)

    nist_helium_lda = -2.834836
    assert abs(result.total_energy - nist_helium_lda) < 0.12
